import os

import pytest

from ..base import BaseTopazTest


class TestProcess(BaseTopazTest):
    def test_euid(self, space):
        w_res = space.execute("return Process.euid")
        assert space.int_w(w_res) == os.geteuid()

    def test_pid(self, space):
        w_res = space.execute("return Process.pid")
        assert space.int_w(w_res) == os.getpid()

    def test_exit(self, space):
        with self.raises(space, "SystemExit"):
            space.execute("Process.exit")
        w_res = space.execute("""
        begin
          Process.exit
        rescue SystemExit => e
          return e.success?, e.status
        end
        """)
        assert self.unwrap(space, w_res) == [True, 0]
        w_res = space.execute("""
        begin
          Process.exit(1)
        rescue SystemExit => e
          return e.success?, e.status
        end
        """)
        assert self.unwrap(space, w_res) == [False, 1]

    @pytest.mark.parametrize("code", [0, 1, 173])
    def test_waitpid(self, space, code):
        pid = os.fork()
        if pid == 0:
            os._exit(code)
        else:
            w_res = space.execute("return Process.waitpid %i" % pid)
            assert space.int_w(w_res) == pid
            w_res = space.execute("return $?")
            status = space.send(w_res, space.newsymbol("to_i"), [])
            assert space.int_w(status) == code

    @pytest.mark.parametrize("code", [0, 1, 173])
    def test_waitpid2(self, space, code):
        pid = os.fork()
        if pid == 0:
            os._exit(code)
        else:
            w_res = space.execute("return Process.waitpid2 %i" % pid)
            [returned_pid, returned_code] = space.listview(w_res)
            assert space.int_w(returned_pid) == pid
            code_to_i = space.send(returned_code, space.newsymbol("to_i"), [])
            assert space.int_w(code_to_i) == code
