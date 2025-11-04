import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.driver.as1620 import AS1620

pb = AS1620(ip="192.168.0.200", port=8081)
pb.open_tree()
# pb.close_tree()

# print(pb.list_bases())