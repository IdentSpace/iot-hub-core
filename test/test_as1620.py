import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.driver.as1620 import AS1620

pb = AS1620(ip="192.168.0.200", port=8081)
# status = pb.open_tree()
# status = pb.close_tree()
status = pb.get_state()


print("Barrier Status: ", status.state, status.message, status.raw_data)

# print(pb.list_bases())