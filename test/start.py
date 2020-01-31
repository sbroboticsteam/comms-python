from Apple      import Apple
from Banana     import Banana
from Canteloupe import Canteloupe
from Durian     import Durian
import sys


MASTERCONFIG = './testconf.json'
HOSTS = {
    "apple": Apple,
    "banana": Banana,
    "canteloupe": Canteloupe,
    "durian": Durian
}


if __name__ == "__main__":
    x = HOSTS[sys.argv[1]](MASTERCONFIG)
    x.run()