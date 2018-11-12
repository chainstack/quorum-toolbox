from constellation import Constellation
import os
import sh
from time import sleep

print("====== START CONSTELLATION TEST =======")
cn = Constellation("company1_q2_n0",
                       "https://10.65.11.96",
                       port=9000,
                       other_nodes=["http://127.0.0.1:9000/", "http://10.11.11.11:9000/"])


print("Created all artifacts and keys need for constellation node. Ready to be launched.")

print("\nKilling any running constellation...")

try:
    sh.killall("constellation-node")
except Exception:
    print("Nothing to kill")

print("Launching constellation with launch script...")
# Note: at this point, constellation can also be launched as cn.launch(), which will take care of changing cwd and etc.
# however, we launch via launch script as during final deployment this is how constellation will be launched.

# can also pass cwd to sh instead of having to change and revert cwd manually.
curr_dir = os.path.abspath(os.curdir)
os.chdir(os.path.join(curr_dir, "company1_q2_n0", "constellation"))

cmd = sh.Command("./launch_constellation.sh")
cmd()

print("Done")
print("\nChecking...")
sleep(5)                                # give some time for constellation to start up

port = ""
with open("constellation.config", "r") as fp:
    for line in fp:
        if "port" in line:
            port = line.split("= ")[1].replace("\n", "")

print("Looking for constellation running at port {0}".format(port))

cmd = sh.netstat.bake("-lupnt")
o = cmd()

stdout = o.stdout.decode(sh.DEFAULT_ENCODING)

found = False
pid = None
for line in stdout.split("\n"):
    if "constellation" in line:
        found = True
        if ":" + str(port) + " " in line:
            pid = line.split(" ")[-1].split("/")[0]
            print(line)
            print("Found constellation running with pid {0} at port {1}".format(pid, port))

if not found:
    raise Exception("Unable to find constellation running")

if pid is None:
    raise Exception("Constellation running...but not at port {0}".format(port))

os.chdir(curr_dir)

print("\nShutting constellation")
sh.kill(pid)

print("If constellation needs to be launched again, use this from constellation directory:")
print(cn.launch_cmd_line)

print("====== PASS =======")
