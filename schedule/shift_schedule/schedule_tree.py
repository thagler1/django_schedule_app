import datetime




# Test

tree = Tree()

for elem in '31415926':
    tree.insert(elem)

print(tree)

print("Preorder traversal: ")
print(list(tree.preOrder()))

print("InOrder Traversal: ")
print(list(tree.inOrder()))

print("PostOrder Traversal: ")
print(list(tree.postOrder()))