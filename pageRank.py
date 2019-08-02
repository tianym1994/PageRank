import  networkx as nx
#用PageRank挖掘希拉里邮件中的重要人物关系
import  pandas as pd
import numpy as np
from  collections import defaultdict
import  matplotlib.pyplot as plt

#数据加载
emils=pd.read_csv('./data/Emails.csv')
#读取识别文件名
file=pd.read_csv('./data/Aliases.csv')
aliases={}
for index,row in file.iterrows():
    aliases[row['Alias']]=row['PersonId']
#读取人名文件
file=pd.read_csv('./data/Persons.csv')
persons={}
for index,row in  file.iterrows():
    persons[row['Id']]=row['Name']
#针对别名进行转换
def unify_name(name):
    #姓名统一小写
    name=str(name).lower()
    #去掉，和@后面的内容
    name=name.replace(',',',').split('@')[0]
    #别名转换
    if name in  aliases.keys():
       return  persons[aliases[name]]
    return  name
#画网络图
def show_graph(graph,layout='spring_layout'):
    #使用Spring layput布局，类似中心放射状
    if layout=='circular_layout':
        positions=nx.circular_layout(graph)
    else:
        positions=nx.spring_layout(graph)
    #设置网络图中的节点大小，大小与pagerank值相关，因为pagerank值很小所以需要*20000
    nodesize=[x['pagerank']*200000 for v,x in graph.nodes(data=True)]
    #设置网络图中边的长度
    edgesize=[np.sqrt(e[2]['weight']) for e in graph.edges(data=True)]
    #绘制节点
    nx.draw_networkx_nodes(graph,positions,node_size=nodesize,alpha=0.4)
    #绘制边
    nx.draw_networkx_edges(graph,positions,edge_size=edgesize,alpha=0.2)
    #绘制节点的label
    nx.draw_networkx_labels(graph,positions,font_size=10)
    #输出希拉里邮件中的所有人物关系图
    plt.show()
#将寄件人和收件人的姓名规范化
emils.MetadataFrom=emils.MetadataFrom.apply(unify_name)
emils.MetadataTo=emils.MetadataTo.apply(unify_name)
#设置边的权重等于发邮件的次数
edges_weights_temp=defaultdict(list)
for row in zip(emils.MetadataFrom,emils.MetadataTo,emils.RawText):
    temp=(row[0],row[1])
    if temp not in edges_weights_temp:
        edges_weights_temp[temp]=1
    else:
        edges_weights_temp[temp]=edges_weights_temp[temp]+1
#转换格式(from,to),weight=>  from,to,weight
edges_weight=[(key[0],key[1],val)  for key,val in edges_weights_temp.items()]
#创建一个有向图
graph=nx.DiGraph()
#设置有向图中的路径及权重(form,to,weight)
graph.add_weighted_edges_from(edges_weight)
#计算每个节点的PR值，并作为结点的pagerank属性
pagerank=nx.pagerank(graph)
#将PageRank的数值作为结点的属性
nx.set_node_attributes(graph,name='pagerank',values=pagerank)
#画网络图
show_graph(graph)
#将完整的图谱简化
#设置PR值的阈值，筛选大于阈值的重要核心节点
pagerank_threshold=0.005
#复制一份计算好的网络图
small_graph=graph.copy()
#剪掉pr值小于PageRank_threshold的节点
for n,p_rank in graph.nodes(data=True):
    if p_rank['pagerank']<pagerank_threshold:
        small_graph.remove_node(n)
#画网络图，采用circular_layout布局让筛选出来的点组成一个圆
show_graph(small_graph,'circular_layout')

