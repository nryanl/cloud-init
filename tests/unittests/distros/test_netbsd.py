import unittest.mock as mock

import pytest
from passlib.hash import bcrypt

import cloudinit.distros.netbsd
from tests.unittests.helpers import get_distro

M_PATH = "cloudinit.distros.netbsd."


class TestNetBSD:
    @pytest.mark.parametrize("distro_name", ["netbsd", "openbsd"])
    @pytest.mark.parametrize("hashed", [True, False])
    @mock.patch(M_PATH + "bcrypt.hash", return_value="hashed-password")
    @mock.patch(M_PATH + "subp.subp")
    def test_set_passwd(self, m_subp, m_hash, hashed, distro_name):
        distro = get_distro(distro_name)
        with mock.patch.object(distro, "unlock_passwd") as m_unlock:
            distro.set_passwd("me2", "password", hashed=hashed)

        if hashed:
            m_hash.assert_not_called()
            expected_password = "password"
        else:
            m_hash.assert_called_once_with("password")
            expected_password = "hashed-password"
        m_subp.assert_called_once_with(
            ["usermod", "-p", expected_password, "me2"]
        )
        m_unlock.assert_called_once_with("me2")

    @mock.patch(M_PATH + "subp.subp")
    def test_set_passwd_bcrypt(self, m_subp):
        distro = get_distro("netbsd")
        distro.set_passwd("me2", "password")

        hashed_password = m_subp.call_args_list[0].args[0][2]
        assert bcrypt.verify("password", hashed_password)
        assert not bcrypt.verify("other-password", hashed_password)

    @mock.patch(M_PATH + "subp.subp")
    def test_add_user(self, m_subp):
        distro = get_distro("netbsd")
        distro.add_user("me2", groups=[], uid=1234, default=False)
        assert [
            mock.call(
                ["useradd", "-m", "me2"], logstring=["useradd", "-m", "me2"]
            )
        ] == m_subp.call_args_list

    @mock.patch(M_PATH + "subp.subp")
    def test_unlock_passwd(self, m_subp, caplog):
        distro = get_distro("netbsd")
        distro.unlock_passwd("me2")
        assert [
            mock.call(["usermod", "-C", "no", "me2"])
        ] == m_subp.call_args_list


@pytest.mark.parametrize("with_pkgin", (True, False))
@mock.patch("cloudinit.distros.netbsd.os")
def test_init(m_os, with_pkgin):
    print(with_pkgin)
    m_os.path.exists.return_value = with_pkgin
    cfg = {}

    # patch ifconfig -a
    with mock.patch(
        "cloudinit.distros.networking.subp.subp", return_value=("", None)
    ):
        distro = cloudinit.distros.netbsd.NetBSD("netbsd", cfg, None)
    expectation = ["pkgin", "-y", "full-upgrade"] if with_pkgin else None
    assert distro.pkg_cmd_upgrade_prefix == expectation
    assert [mock.call("/usr/pkg/bin/pkgin")] == m_os.path.exists.call_args_list
