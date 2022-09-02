import random

class Tree_Manager:
    def __init__(self, num_trees, width, height ):
        self.num_trees = num_trees
        self.width = width
        self.height = height
        self.tree_pos = self.generate_tree_list()

    def generate_tree_list(self):
        output = []
        for iterator in range(self.num_trees):
            result = (round(random.random()*self.width), round(random.random()*self.height))
            output.append(result)
        print("generated ",len(output)," tree positions :", output )
        return output
            
    def get_Tree_Positions(self):
        return self.tree_pos


    def generate_new_tree_pos(self, num_trees):
        self.num_trees = num_trees
        self.tree_pos = self.generate_tree_list()


class Cloud_Manager:
    def __init__(self, numclouds, width, height):
        self.num_clouds = numclouds
        self.cloud_pos = self.generate_initial_clouds()
        self.width = width
        self.height = height

    def generate_tree_list(self):
        output = []
        for iterator in range(self.num_clouds):
            result = (round(random.random()*self.width), round(random.random()*self.height))
            output.append(result)
        print("generated ",len(output)," cloud positions :", output )
        return output