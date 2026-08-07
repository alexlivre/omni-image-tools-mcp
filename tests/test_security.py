"""Security helpers tests: SSRF protection, path resolution, clamping."""

import socket

import pytest

from src.utils.security import (
    MAX_DOWNLOAD_SIZE,
    clamp,
    is_private_ip,
    is_safe_url,
    resolve_safe_path,
)


class TestIsPrivateIp:
    def test_loopback_ipv4(self):
        assert is_private_ip("127.0.0.1") is True

    def test_loopback_ipv6(self):
        assert is_private_ip("::1") is True

    def test_link_local_metadata(self):
        assert is_private_ip("169.254.169.254") is True

    def test_rfc1918_private(self):
        assert is_private_ip("10.0.0.1") is True
        assert is_private_ip("172.16.0.1") is True
        assert is_private_ip("192.168.1.1") is True

    def test_public_ip(self):
        assert is_private_ip("8.8.8.8") is False
        assert is_private_ip("1.1.1.1") is False

    def test_multicast(self):
        assert is_private_ip("224.0.0.1") is True

    def test_ipv6_unique_local(self):
        assert is_private_ip("fc00::1") is True

    def test_invalid_ip_fail_closed(self):
        assert is_private_ip("not-an-ip") is True


class TestIsSafeUrl:
    def test_blocks_metadata_endpoint(self):
        assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False

    def test_blocks_localhost(self):
        assert is_safe_url("http://localhost/admin") is False
        assert is_safe_url("http://127.0.0.1:11434/api/tags") is False

    def test_blocks_private_ip(self):
        assert is_safe_url("http://10.0.0.1/x") is False
        assert is_safe_url("http://192.168.0.1/x") is False

    def test_blocks_non_http_scheme(self):
        assert is_safe_url("file:///etc/passwd") is False
        assert is_safe_url("ftp://example.com/x") is False

    def test_allows_public_https(self):
        assert is_safe_url("https://example.com/image.jpg") is True

    def test_allows_public_http(self):
        assert is_safe_url("http://example.com/image.jpg") is True

    def test_fail_closed_on_dns_resolution_error(self, monkeypatch):
        def fake_getaddrinfo(*a, **k):
            raise socket.gaierror("DNS failed")

        monkeypatch.setattr("src.utils.security.socket.getaddrinfo", fake_getaddrinfo)
        assert is_safe_url("https://does-not-resolve.invalid/x") is False

    def test_blocks_hostname_resolving_to_private(self, monkeypatch):
        def fake_getaddrinfo(host, *a, **k):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 0))]

        monkeypatch.setattr("src.utils.security.socket.getaddrinfo", fake_getaddrinfo)
        assert is_safe_url("https://evil.example.com/x") is False

    def test_allows_hostname_resolving_to_public(self, monkeypatch):
        def fake_getaddrinfo(host, *a, **k):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]

        monkeypatch.setattr("src.utils.security.socket.getaddrinfo", fake_getaddrinfo)
        assert is_safe_url("https://example.com/x") is True

    def test_blocks_empty_and_invalid_urls(self):
        assert is_safe_url("") is False
        assert is_safe_url("not a url") is False
        assert is_safe_url("http://") is False


class TestClamp:
    def test_within_range(self):
        assert clamp(5, 1, 10) == 5

    def test_above_max(self):
        assert clamp(100, 1, 10) == 10

    def test_below_min(self):
        assert clamp(0, 1, 10) == 1

    def test_float(self):
        assert clamp(0.9, 0.0, 1.0) == 0.9
        assert clamp(1.5, 0.0, 1.0) == 1.0

    def test_max_download_size_constant(self):
        assert MAX_DOWNLOAD_SIZE == 20 * 1024 * 1024


class TestResolveSafePath:
    def test_resolves_to_absolute(self, tmp_path):
        f = tmp_path / "img.jpg"
        f.write_bytes(b"x")
        resolved = resolve_safe_path(str(f), allowed_roots=None)
        assert resolved == f.resolve()
        assert resolved.is_absolute()

    def test_blocks_symlink_escape_when_sandboxed(self, tmp_path):
        root = tmp_path / "allowed"
        root.mkdir()
        target = tmp_path / "secret.txt"
        target.write_bytes(b"secret")

        link = root / "escape.jpg"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            pytest.skip("symlinks not supported on this platform")

        with pytest.raises(ValueError, match="outside"):
            resolve_safe_path(str(link), allowed_roots=[root])

    def test_allows_symlink_inside_sandbox(self, tmp_path):
        root = tmp_path / "allowed"
        root.mkdir()
        real = root / "real.jpg"
        real.write_bytes(b"x")
        link = root / "link.jpg"
        try:
            link.symlink_to(real)
        except (OSError, NotImplementedError):
            pytest.skip("symlinks not supported on this platform")

        resolved = resolve_safe_path(str(link), allowed_roots=[root])
        assert resolved.resolve() == real.resolve()

    def test_permissive_when_no_sandbox(self, tmp_path):
        f = tmp_path / "img.png"
        f.write_bytes(b"x")
        resolved = resolve_safe_path(str(f), allowed_roots=None)
        assert resolved.is_file()

    def test_nonexistent_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            resolve_safe_path(str(tmp_path / "nope.jpg"), allowed_roots=None)
