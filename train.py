import numpy as np
import math

def distance(vector1,vector2):
    dist=0
    for i in range(49):
        dist+=(vector1[i]-vector2[i])**2
    return math.sqrt(dist)

def calculateActivationLevel(docVec,processor,processorLink):
    activeProcessors=[]
    for p,neighbours in processorLink.items():
        #print(p)
        #print(neighbours)
        c=len(neighbours)
        s=0.0
        for n in neighbours:
            s+=distance(processor[p],processor[n])
        a=s/c
        if distance(docVec,processor[p])<=a:
            activeProcessors.append(p)
    return activeProcessors

def winner(candidateProcessor,processor,docVec):
    minVec=9999
    winnerId=0
    Wu=0
    for c in candidateProcessor:
        if distance(docVec,processor[c])<minVec:
            minVec=distance(docVec,processor[c])
            winnerId=c
    Wu=processor[winnerId]
    return winnerId,Wu

def secondWinner(processor,winnerId,docVec):
    minVec=9999
    secondWinnerId=0
    Wv=list()
    for i in range(49):
        Wv.append(0)
        
    for p,w in processor.items():
        if (p != winnerId) and (distance(docVec,w)<minVec):
            minVec=distance(docVec,processor[p])
            secondWinnerId=p
    if(secondWinnerId):
        Wv=processor[secondWinnerId]
    return secondWinnerId,Wv                           

def diffList(list1,list2):
    l=[]
    for i in range(49):
        l.append(list1[i]-list2[i])
    return l

def multList(c,list1):
    l=[]
    for e in list1:
        l.append(c*e)
    return l

def addList(list1,list2):
    l=[]
    for i in range(49):
        l.append(list1[i]+list2[i])
    return l

def union(l,p):
    newl=[]
    for e in l:
        if e!=p:
            newl.append(e)
    newl.append(p)
    return newl

def TASONN(sId,documents,s=4.5,d=8,a1=.9,a2=.9):    # mention the value of s-level & d if you do not pass as parameters.
    processor=dict()
    processorLinks=dict()    
    
    
    for phase in range(10):
        
        print('s#: '+sId+' phase=',phase)
        t=0        
        print('s#: '+sId+' processor#: '+str(len(processor)))        
            
        for docVec in documents:
            t=t+1  
 
            #activeProcessors=calculateActivationLevel(docVec,processor,processorLinks)
            candidateProcessor=list()

            for p in processor:
                if distance(processor[p],docVec)<=s:
                    candidateProcessor.append(p)            
            if(len(candidateProcessor)==0):
                processor['p'+str(sId)+str(phase)+str(t)]=docVec
                winnerId='p'+str(sId)+str(phase)+str(t)                
                Wu=docVec[0:49]
            elif len(candidateProcessor) is 1:
                winnerId=candidateProcessor[0]
                Wu=processor[candidateProcessor[0]]
            else:
                winnerId,Wu=winner(candidateProcessor,processor,docVec)

            secondWinnerId,Wv=secondWinner(processor,winnerId,docVec)
            
            Wu1=addList(Wu, multList(a1, diffList(docVec,Wu) ) )
            Wv1=addList(Wv, multList(a2, diffList(docVec,Wv) ) )
            
            processor[winnerId]=Wu1
            if secondWinnerId:
                processor[secondWinnerId]=Wv1
                
                try:    
                    processorLinks[winnerId]=union(processorLinks[winnerId],secondWinnerId)                    
                except:
                    processorLinks[winnerId]=[secondWinnerId]
                    
                try:
                    processorLinks[secondWinnerId]=union(processorLinks[secondWinnerId],winnerId)
                except:
                    processorLinks[secondWinnerId]=[winnerId]                
            
        processorInsertInBetween=list()
        flag=True
        for p,neighbours in processorLinks.items():
            for n in neighbours:
                if (distance(processor[p],processor[n])>=d) and ( (n,p) not in processorInsertInBetween): 
                    flag=False
                    processorInsertInBetween.append((p,n))
        if flag:
            print("converged")
            break
        print('s#: '+sId+" processorInsertInBetween")
        for p,n in processorInsertInBetween:             
            pId=p+n
            processor[pId]=multList(.5,addList(processor[p],processor[n]))
            processorLinks[p].append(pId)
            processorLinks[pId]=[p]
            processorLinks[n].append(pId)
            processorLinks[pId].append(n)            
            processorLinks[p].remove(n)
            processorLinks[n].remove(p)
        print('s#: '+sId+' processor#: '+str(len(processor)))
        
    print('s#: '+sId+' processor#: '+str(len(processor)))    
    for pId,weight in processor.items():
        processor_file.write(sId+'\t'+pId+'\t')
        for w in weight:
            processor_file.write(str(w)+' ')
        processor_file.write('\n')

import time
import threading
import os

dir_name="cw09-shards"
shards_dir= os.listdir(dir_name+'/')
print(shards_dir)
threads=[]
c=0
start=0
end=0
#output_file=input('enter the name of the output file: ')
processor_file=open('processors4',"w+")
for i in range(0,92):    
    documents=[]
    shard_file=open(dir_name+'/'+shards_dir[i],"r")    
    for line in shard_file:
        parts=line.split('\t')
        sId=parts[0]
        docId=parts[1]
        docVec=parts[2]
        docVec=docVec.split(' ')
        docVec=[float(i) for i in docVec]
        documents.append(docVec)
    shard_file.close()
    start=time.time()  

#comment the following 2 lines if you do not want different s-level & d for diferent shards & please remove the params during function call.  
    #s=int(input("Enter the sensitivity level for shard "+shards_dir[i]+": "))
    #d=int(input("Enter the max distance allowed between any 2 processors for shard "+shards_dir[i]+": "))
    print("processing started for shard: "+shards_dir[i])
    TASONN(sId,documents)    
    print("shard #"+sId+' completed') 
    end=time.time()
    print("time taken: "+str(end-start))

#If you want to use multi-threading then uncomment the following lines.
    #t=threading.Thread(target=TASONN, args=(sId,documents)) 
    #t.start()        
    #threads.append(t)
    #c+=1
#for t in threads:
    #t.join()  
    #print(str(t)+' joined')
	
print("training complete")
