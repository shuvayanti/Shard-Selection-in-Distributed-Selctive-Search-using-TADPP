import math
import numpy as np
import time

def cos_sim(vector1,vector2):
    dotProduct=0.0
    sumV1=0.0
    sumV2=0.0
    for i in range(len(vector2)):
        dotProduct+=vector1[i]*vector2[i]
        sumV1+=vector1[i]**2
        sumV2+=vector2[i]**2
    if sumV1*sumV2==0:
        cosine_similarity=0
    else:
        cosine_similarity=dotProduct/math.sqrt(sumV1*sumV2) 
    return cosine_similarity

def L_ensemble(processor,query):
    Lmatrix=[ [0 for col in range(len(processor))] for row in range(len(processor))]
    for i,pi in enumerate(processor.keys()):
        for j,pj in enumerate(processor.keys()):
            Lmatrix[i][j]=cos_sim(processor[pi],query)*cos_sim(processor[pj],query) #*cos_sim(processor[pi],processor[pj])           
    return Lmatrix

def union(l,p):
    newl=[]
    for e in l:
        if e!=p:
            newl.append(e)
    newl.append(p)
    return newl

def Score(Lmatrix,S,p_keys):
    score=0
    indices=[]    
    for e in S:
        indices.append(p_keys.index(e))
    
    dummy=[[0 for col in range(len(indices))] for row in range(len(indices))]
    
    for i,i1 in enumerate(indices):        
        for j,i2 in enumerate(indices):
            dummy[i][j]=Lmatrix[i1][i2]
    
    if dummy==[]:
        return 0

    a=np.array(dummy)    
    determinant=np.linalg.det(a)
    score=10**determinant
    #if determinant==0:
        #score=-99999
    #elif determinant>0:        
        #score=math.log10(determinant)
    return score

def DPP_rank(processor,shard,query):
	Lmatrix=L_ensemble(processor,query)
	S=list()
	potential_shards_score=dict()
	potential_shards_count=dict()
	i=0
	p_keys=list(processor.keys())
	while i<75:        #top-50 processors will be selected     
		i+=1
		max_score=0
		potential_p=""
		#found=False
		for p in p_keys:
			if p not in S:
				snew=union(S,p)
				scoreL=Score(Lmatrix,snew,p_keys)
				if scoreL>max_score:
					#found=True					
					max_score=scoreL
					potential_p=p
				#print(max_score)
		print(potential_p)
		#if found==False:
			#break
		
		S=union(S,potential_p)		
		potential_s=shard[potential_p]		
		try:
			potential_shards_score[potential_s]+=max_score
			potential_shards_count[potential_s]+=1
		except:
			potential_shards_score[potential_s]=max_score
			potential_shards_count[potential_s]=1
	
	return potential_shards_score,potential_shards_count

#query_file_name=input("Enter the query file name: ")
#processor_file_name=input("Enter the processor_file_name: ")


processor_file=open('processors3(s=4.7,d=8)',"r")
processor_vector={}
processor_shard={}
for line in processor_file:
    p_parts=line.split('\t')
    sId=p_parts[0]
    pId=p_parts[1]
    pVec=p_parts[2]
    pVec=pVec.split(' ')
    pVec.remove('\n')
    pVec=[float(i) for i in pVec]
    processor_vector[pId]=pVec
    processor_shard[pId]=sId
#print(len(processor_vector))
#print(len(processor_shard))

#shard_file_name_score=input("Enter the name of the selected shards file(based on score):")
#shard_file_name_count=input("Enter the name of the selected shards file(based on count):")
shard_selected_score=open('selected_shards_score',"w+")
shard_selected_count=open('selected_shards_count',"w+")
shard_selected_count_score=open('selected_shards_count&score',"w+")
query_file=open('cw09b-query-vectors').read().splitlines() 
#print(len(query_file))

for i in range(0,3): 
	#shards=[]   
	start=time.time()
	query=query_file[i].split(' ')
	qVec=[]
	qId=query[0]
	print(qId+" started")
	for i in range(1,len(query)):
		q=float(query[i])
	qVec.append(q)
	
	shards_count_score=dict()
	shards_score,shards_count=DPP_rank(processor_vector,processor_shard,qVec)
	#print(shards_score)
	#print(shards_count)
	for s in shards_count.keys():
		#print(s)
		#print(shards_score[s])
		shards_count_score[s]=shards_score[s]+shards_count[s]
	shard_selected_score.write(qId+'\t')
	shard_selected_count.write(qId+'\t')
	shard_selected_count_score.write(qId+'\t')
	#for p in S:
		#shards=union(shards,processor_shard[p])
	sorted_shards_score=sorted(shards_score.items(), key=lambda kv: kv[1],reverse=True)
	sorted_shards_count=sorted(shards_count.items(), key=lambda kv: kv[1],reverse=True)
	sorted_shards_count_score=sorted(shards_count_score.items(), key=lambda kv: kv[1],reverse=True)
	for s in sorted_shards_score:	
		#shard_selected.write(p+'('+processor_shard[p]+'),\t')
		shard_selected_score.write(s[0]+'('+str(s[1])+')'+',\t')
	shard_selected_score.write('\n')
	
	for s in sorted_shards_count:	
		shard_selected_count.write(s[0]+'('+str(s[1])+')'+',\t')
	shard_selected_count.write('\n')
	
	for s in sorted_shards_count_score:	
		shard_selected_count_score.write(s[0]+'('+str(s[1])+')'+',\t')
	shard_selected_count_score.write('\n')
	
	print("query#: "+qId+" is done.")
	end=time.time()
	print("time taken: "+str(end-start))
