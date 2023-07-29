import tqdm
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString

class TQDMBytesReader(object):

    def __init__(self, fd, **kwargs):
        self.fd = fd
        from tqdm import tqdm
        self.tqdm = tqdm(**kwargs, desc="Reading Pickled Cache File...")

    def read(self, size=-1):
        bytes = self.fd.read(size)
        self.tqdm.update(len(bytes))
        return bytes

    def readline(self):
        bytes = self.fd.readline()
        self.tqdm.update(len(bytes))
        return bytes

    def __enter__(self):
        self.tqdm.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        return self.tqdm.__exit__(*args, **kwargs)


class Comparison:
    def __init__(self, user1, image1, user2, image2, score):
        self.user1 = user1
        self.user2 = user2
        self.image1 = image1
        self.image2 = image2
        self.score = 1 - score


def get_arranged_list():
    if os.path.isfile('./arranged.pickle'):
        with open('arranged.pickle', 'rb') as fd:
            total = os.path.getsize('arranged.pickle')
            with TQDMBytesReader(fd, total=total) as pickle_file_handle:
                up = pickle.Unpickler(pickle_file_handle)
                obj = up.load()
            return obj

    all = []
    with tqdm.tqdm(total=os.path.getsize('all.txt'), desc="Reading File... all.txt") as pbar:
        with open('all.txt', 'r') as file:
            for line in file:
                pbar.update(len(line.encode('utf-8')))
                all.append(line)
            file.close()

    def get_extract(line):
        a, b, score, d = line.strip().split(" ")
        _, __, u1, i1 = a.split("_")
        _, __, u2, i2 = b.split("_")
        return Comparison(int(u1), int(i1.split('.')[0]), int(u2), int(i2.split('.')[0]), float(score))

    temp_objects = list(get_extract(x) for x in tqdm.tqdm(all, total=len(all), desc="Loading Scores...."))
    with open('arranged.pickle', 'wb') as f:
        pickle.dump(temp_objects, f)
    return temp_objects


arranged = get_arranged_list()

intra = {}
inter = {}
minScore = float('inf')
maxScore = float('-inf')
for comparison in tqdm.tqdm(arranged, desc="Calculating Intra and inter"):
    if comparison.image1 > 2 or comparison.image2 > 2:
        continue
    if comparison.score:
        minScore = min(minScore, comparison.score)
    maxScore = max(maxScore, comparison.score)
    if comparison.user1 == comparison.user2:
        if comparison.user1 not in intra:
            intra[comparison.user1] = []
        intra[comparison.user1].append(comparison.score)
    else:
        user1 = comparison.user1
        user2 = comparison.user2
        score = comparison.score
        if user1 not in inter:
            inter[user1] = {}
        if user2 not in inter:
            inter[user2] = {}
        if user2 not in inter[user1]:
            inter[user1][user2] = []
        if user1 not in inter[user2]:
            inter[user2][user1] = []
        inter[user1][user2].append(score)
        inter[user2][user1].append(score)

users = list(range(0, 60))
p = (maxScore - minScore) / (len(users) - 1)
genuine_list = list(y for x in intra.values() for y in x)
imposter_list = list(z for x in inter.values() for y in x.values() for z in y)
thresholds = list(minScore + (i * p) for i in range(60))
fartotals = []
frrtotals = []
import collections
for t in thresholds:
    frr = float(len(list(True for intra_score in genuine_list if intra_score < t))) / len(genuine_list)
    far = float(len(list(True for inter_score in imposter_list if inter_score > t))) / len(imposter_list)
    frrtotals.append(frr)
    fartotals.append(far)

def getThreshold():
    frr_numpy_array = np.array(frrtotals)
    far_numpy_array = np.array(fartotals)
    first_line = LineString(np.column_stack((frr_numpy_array, frr_numpy_array)))
    second_line = LineString(np.column_stack((frr_numpy_array, far_numpy_array)))
    intersection = first_line.intersection(second_line)
    if intersection.geom_type == 'MultiPoint':
        raise Exception("CODE INVALID")
    return intersection.x

def getEER():
    thresholds_numpy_array = np.array(thresholds)
    frr_numpy_array = np.array(frrtotals)
    far_numpy_array = np.array(fartotals)
    first_line = LineString(np.column_stack((thresholds_numpy_array, frr_numpy_array)))
    second_line = LineString(np.column_stack((thresholds_numpy_array, far_numpy_array)))
    intersection = first_line.intersection(second_line)
    if intersection.geom_type == 'MultiPoint':
        raise Exception("CODE INVALID")
    return intersection.x

def SHOW_AUC_CURVE_GRAPH():
    EER = getEER()
    THRESHOLD = getThreshold()
    plt.plot(thresholds,frrtotals,label = "frr",color='green')
    plt.plot(thresholds,fartotals, label="far",color='magenta')
    plt.title("Threshold = {} , EER = {}".format(THRESHOLD,EER))
    plt.get_current_fig_manager().set_window_title("Threshold = {} , EER = {}".format(THRESHOLD,EER))
    plt.gca().legend()
    plt.gca().set_facecolor("lightgrey")
    plt.grid()
    plt.show()


def show_ROC_CURVE():
    import matplotlib.pyplot as plt
    plt.plot(fartotals,frrtotals,color='magenta')
    plt.title("ROC curve")
    plt.get_current_fig_manager().set_window_title("ROC curve")
    plt.gca().set_facecolor("lightgrey")
    plt.grid()
    plt.show()

SHOW_AUC_CURVE_GRAPH()
show_ROC_CURVE()

def probabilityGraph():
    totalMax = max(max(imposter_list),max(genuine_list))
    totalMin = min(min(imposter_list),min(genuine_list))
    stepSize = (totalMax -totalMin)/50
    start = totalMin
    x_axis = []
    genuine_axis = []
    imposter_axis = []
    tuples=[]
    while start<=totalMax:
        end = start + stepSize
        genuine_axis.append( sum(1 for score in genuine_list if start<=score<end) / len(genuine_list))
        imposter_axis.append( sum(1 for score in imposter_list if start<=score<end) / len(imposter_list))
        x_axis.append((start+end)//2)
        tuples.append(
            (
                    (start + end) // 2,
                    sum(1 for score in genuine_list if start <= score < end) / len(genuine_list),
                    sum(1 for score in imposter_list if start <= score < end) / len(imposter_list)
            )
        )
        start += stepSize
    import matplotlib.pyplot as plt
    import numpy as np
    plt.hist(np.array(genuine_axis),label="GENUINE",color='magenta')
    plt.hist(np.array(imposter_axis),label="IMPOSTER",color='green')
    plt.legend()
    plt.gca().set_facecolor("lightgrey")
    plt.grid()
    plt.show()


def hist():
    totalDiv = 500
    step = (maxScore - minScore) / totalDiv
    x_axis_density = []
    far_densitys = []
    frr_densitys = []
    for i in range(totalDiv):
        mininterval = minScore + i * step
        maxinterval = minScore + (i + 1) * step
        frr_probability_density = sum(1 for point in genuine_list if mininterval <= point < maxinterval) / len(genuine_list)
        far_probability_density = sum(1 for point in imposter_list if mininterval <= point < maxinterval) / len(imposter_list)
        far_densitys.append(far_probability_density)
        frr_densitys.append(frr_probability_density)
        x_axis_density.append((mininterval + maxinterval) / 2)


    import matplotlib.pyplot as plt
    plt.plot(x_axis_density, far_densitys, label="GENUINE PROBABILITY DENSITY")
    plt.plot(x_axis_density, frr_densitys, label="IMPOSTER PROBABILITY DENSITY")
    plt.gca().legend((" IMPOSTER PROBABILITY DENSITY","GENUINE PROBABILITY DENSITY"))
    plt.get_current_fig_manager().set_window_title('PROBABILITY DENSITY GRAPH')
    plt.gca().set_facecolor("lightgrey")
    plt.grid()
    plt.show()

    # import matplotlib.pyplot as plt
    # plt.title("FAR")
    # plt.hist(far_densitys)
    # plt.gca().set_facecolor("lightgrey")
    # plt.grid()
    # plt.show()
    #
    # import matplotlib.pyplot as plt
    # plt.title("FRR")
    # plt.hist(frr_densitys)
    # plt.gca().set_facecolor("lightgrey")
    # plt.grid()
    # plt.show()

hist()