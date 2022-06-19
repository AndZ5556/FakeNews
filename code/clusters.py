import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import random
import copy
import csv
from sklearn.decomposition import PCA

# n = 2
# dim = 2
# k = 300

class Clusterization:
    def clusterization(self, array, test_clusters):
        n = len(array)
        dim = 2
        k = 2

        cluster = [[0 for i in range(dim)] for q in range(k)]

        for i in range(dim):
            for q in range(k):
                cluster[q][i] = random.randint(0, 100) / 100

        cluster_content = self.data_distribution(array, cluster, n, k, dim)

        previous_cluster = copy.deepcopy(cluster)
        while 1:
            cluster = self.cluster_update(cluster, cluster_content, dim)
            cluster_content = self.data_distribution(array, cluster, n, k, dim)
            if cluster == previous_cluster:
                break
            previous_cluster = copy.deepcopy(cluster)
        self.visualization(cluster_content, test_clusters)



    def cluster_update(self, cluster, cluster_content, dim):
        k = len(cluster)
        for i in range(k): #по i кластерам
            for q in range(dim): #по q параметрам
                updated_parameter = 0
                for j in range(len(cluster_content[i])):
                    updated_parameter += cluster_content[i][j][q]
                if len(cluster_content[i]) != 0:
                    updated_parameter = updated_parameter / len(cluster_content[i])
                cluster[i][q] = updated_parameter
        return cluster


    def data_distribution(self, array, cluster, n, k, dim):
        cluster_content = [[] for i in range(k)]

        for i in range(n):
            min_distance = float('inf')
            situable_cluster = -1
            for j in range(k):
                distance = 0
                for q in range(dim):
                    distance += (array[i][q] - cluster[j][q]) ** 2

                distance = distance ** (1 / 2)
                if distance < min_distance:
                    min_distance = distance
                    situable_cluster = j

            cluster_content[situable_cluster].append(array[i])

        return cluster_content

    def visualisation_2d(self, cluster_content):
        def sort(a):
            return len(a)
        cluster_content = sorted(cluster_content, key=sort)
        k = len(cluster_content)
        colors = ['red', 'green']
        for i in range(k):
            x_coordinates = []
            y_coordinates = []
            for q in range(len(cluster_content[i])):
                x_coordinates.append(cluster_content[i][q][0])
                y_coordinates.append(cluster_content[i][q][1])
            plt.scatter(x_coordinates, y_coordinates, color=colors[i])
            plt.xlabel("Количетсво ретвитов")
            plt.ylabel("Глубина распространения")


    def visualization(self, cluster_content, test_clusters):
        plt.grid()
        plt.xlabel("x")
        plt.ylabel("y")
        plt.subplot(1, 2, 1)
        self.visualisation_2d(cluster_content)
        plt.subplot(1, 2, 2)
        self.visualisation_2d(test_clusters)
        plt.show()


# rows = []
# array = []
# clusters = [[], []]
# max_users = 1
# max_size = 1
# with open('result/learning/result.csv', 'r') as csv_file:
#     reader = csv.DictReader(csv_file)
#     for element in reader:
#         rows.append(element)
#         if max_users < int(element['Users']):
#             max_users = int(element['Users'])
#         if max_size < int(element['Size']):
#             max_size = int(element['Size'])
#     for element in rows:
#         data = [int(element['Depth']) / 15, int(element['Size']) / max_size, int(element['Users']) / max_users]
#         if element['Type'] == 'fake':
#             clusters[0].append(data)
#         else:
#             clusters[1].append(data)
#         array.append(data)
# print('Start Clusterization')
# pca = PCA(n_components = 2)
# np_array = np.array(array)
# # np_array = pca.fit(np_array).transform(np_array)
# Clusterization().clusterization(np_array, clusters)




