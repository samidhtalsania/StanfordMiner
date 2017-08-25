import urllib
from bs4 import BeautifulSoup
import ipdb
import pymongo
from pymongo import MongoClient
import time

class Node(object):

	def __init__(self, name = '', size = 0, children = None):
		self.name = name
		self.size = 0
		self.nodeset = dict()

	def set_size(self, size):
		self.size = size

	def get_set(self):
		return self.nodeset;


	def __eq__(self, other):
	    return self.name == other.name
	
	def __hash__(self):
	    return hash(self.name)


class Tree(object):
	def __init__(self):
		self.root = Node()

	def insert(self, name, size):
		children = self.root.get_set()
		names = name.split(" > ")

		for x in range(0, len(names)):
			curr = names[x]

			if children.has_key(curr):
				child = children.get(curr)
				if x == len(names) - 1:
					child.set_size(size)

			else:
				new_node = Node(curr, 0)
				if x == len(names) - 1:
					new_node.set_size(size)
				children[curr] = new_node

			children = children[curr].get_set()

	def traverse(self, node):
		# ipdb.set_trace()
		l = []
		l.append("{")
		# l.append(string)
		l.append('"name":"')
		l.append(node.name)
		l.append('",')
		l.append('"size":"')
		l.append(str(node.size))
		l.append('",')
		# l.append(string)
		l.append('"children":[')
		for x in node.get_set().values():
			# l.append(string)
			l.append(self.traverse(x))
			l.append(",")

		if len(node.get_set().values()) > 0:
			l = l[:-1]

		# l.append(string)
		l.append("]")
		# l.append(string)
		l.append("}")
		return ''.join(l)

	def pprint(self):
		children = self.root.get_set()
		return self.traverse(children[children.keys()[0]])

	
def getRoot(root_id, title_str, level):
	
	tries = 0
	while tries < 5:
		try:
			res = urllib.urlopen(base_url+str(root_id))
			html = res.read()
			soup = BeautifulSoup(html, 'xml')


			title = soup.synset['words'].strip()

			size = int(soup.synset['subtree_size'])

			# ipdb.set_trace()

			if len(title_str) != 0:
				title = title_str + " > " +title

			addToDatabase(title, size - 1)

			for synset in soup.find_all('synset')[1:]:
				getRoot(synset['synsetid'],  title)
			
			failed.remove(root_id)

		except IOError:
			time.sleep(1)
			tries = tries + 1
			failed.add(root_id)
			continue;

		except KeyError:
			break

		break

def addToDatabase(title, size):
	post = {"name": title, "size": size}
	db.tree.insert_one(post)

def createTree(tree, db):
	cursor = db.tree.find({})
	# count = 0
	for document in cursor:
		tree.insert(document['name'], document['size'])




def main():
	base_url = 'http://imagenet.stanford.edu/python/tree.py/SubtreeXML?rootid='
	client = MongoClient()
	db = client.mydb

	failed = set()

	getRoot(82127, '')

	tree = Tree()
	createTree(tree, db)
	file = open("testfile.txt", "w")
	file.write(tree.pprint())
	file.close()


if __name__ == '__main__':
	main()



