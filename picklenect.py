import pickle
import freenect

data = freenect.sync_get_depth()
pickle.dump("data.txt",data)
