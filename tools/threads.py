#!/usr/bin/env python3
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import statistics
import subprocess
from utils.runner import *
from utils.perfapp import *

class ThreadRunner(TestRunner):
    __summary = {}
    __app = None
    def run(self):
        self.__app = self.__get_app()

        for f in self.files:
            self.__test(f)

        self.__print_summary()

    def add_args(self, parser):
        parser.add_argument("--vvdec-path", type=str)

    def __get_app(self):
        if self.args.vvdec_path:
            return VVDecApp(self.args.vvdec_path)
        return FFmpegApp(self.args.ffmpeg_path)

    def __test(self, input):
        fn = os.path.basename(input)
        self.__summary[fn] = [[], []]
        for i in [1, 0]:
            fps = self.__summary[fn][i]
            for j in [16, 8, 4, 2, 1]:
                self.__app.set_asm(i)
                self.__app.set_threads(j)
                cmd = self.__app.get_cmd(input)
                print(cmd)
                try:
                    o = subprocess.run(cmd.split(), capture_output=True, timeout=5 * 60)
                    if o.returncode:
                        raise Exception(o.stderr)
                    o = self.__app.get_fps(o)
                    print("fps = ", o)
                    fps.append(o)
                except Exception as e:
                    print(e)
                    raise

    def __print_summary(self):
        for k,v in self.__summary.items():
            print_summary(k, "no asm", v[0])
            print_summary(k, "with asm", v[1])
        pass

def print_summary(fn, msg, a):
    s = fn + ", " + msg + " fps : {"
    for fps in a:
        s += " " + str(fps) + ","
    s += " }"
    print(s)

if __name__ == "__main__":
    t = ThreadRunner()
    t.check_input()
    t.run()
