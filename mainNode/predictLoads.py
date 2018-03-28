
import matplotlib.pyplot as plt
import numpy as np
import random
import time

#An example of a class
class Network:

    def __init__(self, Topo, Train, Test, MaxTime, Samples, MinPer):
        self.Top  = Topo  # NN topology [input, hidden, output]
        self.Max = MaxTime # max epocs
        self.TrainData = Train
        self.TestData = Test
        self.NumSamples = Samples

        self.lrate  = 0 # will be updated later with BP call

        self.momenRate = 0
        self.useNesterovMomen = 0 #use nestmomentum 1, not use is 0

        self.minPerf = MinPer
                                        #initialize weights ( W1 W2 ) and bias ( b1 b2 ) of the network
        np.random.seed()
        self.W1 = np.random.randn(self.Top[0]  , self.Top[1])  / np.sqrt(self.Top[0] )
        self.B1 = np.random.randn(1  , self.Top[1])  / np.sqrt(self.Top[1] ) # bias first layer
        self.BestB1 = self.B1
        self.BestW1 = self.W1
        self.W2 = np.random.randn(self.Top[1] , self.Top[2]) / np.sqrt(self.Top[1] )
        self.B2 = np.random.randn(1  , self.Top[2])  / np.sqrt(self.Top[1] ) # bias second layer
        self.BestB2 = self.B2
        self.BestW2 = self.W2
        self.hidout = np.zeros((1, self.Top[1] )) # output of first hidden layer
        self.out = np.zeros((1, self.Top[2])) #  output last layer


    def sigmoid(self,x):
        return 1 / (1 + np.exp(-x))

    def sampleEr(self,actualout):
        error = np.subtract(self.out, actualout)
        sqerror= np.sum(np.square(error))/self.Top[2]
        #print sqerror
        return sqerror

    def ForwardPass(self, X ):
         z1 = X.dot(self.W1) - self.B1
         self.hidout = self.sigmoid(z1) # output of first hidden layer
         z2 = self.hidout.dot(self.W2)  - self.B2
         self.out = self.sigmoid(z2)  # output second hidden layer



    def BackwardPassMomentum(self, Input, desired, vanilla):
            out_delta =   (desired - self.out)*(self.out*(1-self.out))
            hid_delta = out_delta.dot(self.W2.T) * (self.hidout * (1-self.hidout))

            if vanilla == 1: #no momentum
                self.W2+= (self.hidout.T.dot(out_delta) * self.lrate)
                self.B2+=  (-1 * self.lrate * out_delta)
                self.W1 += (Input.T.dot(hid_delta) * self.lrate)
                self.B1+=  (-1 * self.lrate * hid_delta)

            else:
                v2 = self.W2 #save previous weights http://cs231n.github.io/neural-networks-3/#sgd
                v1 = self.W1
                b2 = self.B2
                b1 = self.B1
                v2 = ( v2 *self.momenRate) + (self.hidout.T.dot(out_delta) * self.lrate)       # velocity update
                v1 = ( v1 *self.momenRate) + (Input.T.dot(hid_delta) * self.lrate)
                v2 = ( v2 *self.momenRate) + (-1 * self.lrate * out_delta)       # velocity update
                v1 = ( v1 *self.momenRate) + (-1 * self.lrate * hid_delta)

                if self.useNesterovMomen == 0: # use classical momentum
                    self.W2+= v2
                    self.W1 += v1
                    self.B2+= b2
                    self.B1 += b1

                else: # useNesterovMomen http://cs231n.github.io/neural-networks-3/#sgd
                    v2_prev = v2
                    v1_prev = v1
                    self.W2+= (self.momenRate * v2_prev + (1 + self.momenRate) )  * v2
                    self.W1 += ( self.momenRate * v1_prev + (1 + self.momenRate) )  * v1



    def TestNetwork(self, Data, testSize):
        output = []
        target = []
        Input = np.zeros((1, self.Top[0])) # temp hold input
        Desired = np.zeros((1, self.Top[2]))
        nOutput = np.zeros((1, self.Top[2]))

        sse = 0
        self.W1 = self.BestW1
        self.W2 = self.BestW2 #load best knowledge
        self.B1 = self.BestB1
        self.B2 = self.BestB2 #load best knowledge

        for s in range(0, testSize):

            Input[:]  =   Data[s,0:self.Top[0]]
            Desired[:] =  Data[s,self.Top[0]:]

            self.ForwardPass(Input )
            #output.append(self.out[0])
            #o = Desired[0]
            #target.append(o[0])
            sse = sse+ self.sampleEr(Desired)


        return ( (sse/testSize), output, target )


    def saveKnowledge(self):
        self.BestW1 = self.W1
        self.BestW2 = self.W2
        self.BestB1 = self.B1
        self.BestB2 = self.B2

    def BP_GD(self, learnRate, mRate,  useNestmomen , stocastic, vanilla): # BP with SGD (Stocastic BP)
        self.lrate = learnRate
        self.momenRate = mRate
        self.useNesterovMomen =  useNestmomen

        Input = np.zeros((1, self.Top[0])) # temp hold input
        Desired = np.zeros((1, self.Top[2]))
        #print(Desired)
        Er = []#np.zeros((1, self.Max))
        epoch = 0
        bestrmse = 1
        while  epoch < self.Max and bestrmse> self.minPerf :

            sse = 0
            for s in range(0, self.NumSamples):

                if(stocastic):
                   pat = random.randint(0, self.NumSamples-1)
                else:
                   pat = s

                Input[:]  =  self.TrainData[pat,0:self.Top[0]]
                Desired[:] = [self.TrainData[pat,self.Top[0]:]]



                self.ForwardPass(Input )
                self.BackwardPassMomentum(Input , Desired, vanilla)
                sse = sse+ (self.sampleEr(Desired))

            rmse = (sse/self.NumSamples*self.Top[2])

            if rmse < bestrmse:
               bestrmse = rmse
               self.saveKnowledge()


            Er = np.append(Er, rmse)


            epoch=epoch+1

        return (Er,bestrmse,  epoch)




def main():

    outfile = open('FNN_results-0-249-2' ,'w')

    for host in range(250):
        Hidden = 10
        Input = 24  #
        Output = 6
        TrSamples = 7530 - Input - Output
        TestSize = 198
        learnRate = 0.1
        mRate = 0.01
        MaxTime = 100


        infile = open('C:\\Users\\FLI-2016\\Documents\\Research\\NeuralNetwork\\Google\\ActualTraces\\Host'+str(host), 'r')
        data = infile.readlines()
        infile.close()
        for q in range(len(data)):
            data[q] = float(data[q].rstrip('\n'))
        TrainData  = []
        TestData  = []

        for i in range(TrSamples):
            TrainData.append(data[i:i+Input+Output])
        #print(TrainData[0])
        for i in range(TrSamples+Input+Output,len(data)-Input-Output):
            TestData.append(data[i:i+Input+Output])
        #print(TrainData)
        TrainData = np.array(TrainData)
        TestData = np.array(TestData)
        TestSize = len(TestData)



        Topo = [Input, Hidden, Output]
        MaxRun = 1 # number of experimental runs

        MinCriteria = 0.0005 #stop when RMSE reaches MinCriteria ( problem dependent)


        useStocasticGD = 0 # 0 for vanilla BP. 1 for Stocastic BP
        useVanilla = 1 # 1 for Vanilla Gradient Descent, 0 for Gradient Descent with momentum (either regular momentum or nesterov momen)
        useNestmomen = 0 # 0 for regular momentum, 1 for Nesterov momentum




        trainRMSE =  np.zeros(MaxRun)
        testRMSE =  np.zeros(MaxRun)
        Epochs =  np.zeros(MaxRun)
        Time =  np.zeros(MaxRun)

        for run in range(0, MaxRun  ):
            #print (run)
            fnnSGD = Network(Topo, TrainData, TestData, MaxTime, TrSamples, MinCriteria) # Stocastic GD
            start_time=time.time()
            (erEp,  trainRMSE[run] ,  Epochs[run]) = fnnSGD.BP_GD(learnRate, mRate, useNestmomen,  useStocasticGD, useVanilla)
            Time[run]  =time.time()-start_time
            (testRMSE[run], predicted, actual ) = fnnSGD.TestNetwork(TestData, TestSize )


        #print (trainRMSE)
        #print (testRMSE)

        #print Epochs
        #print Time
        #print(np.mean(trainRMSE), np.std(trainRMSE))
        print('Host'+str(host)+': ', np.mean(testRMSE), np.std(testRMSE))
        #print(np.mean(Time), np.std(Time))
        outfile.write('Host'+str(host)+','+str(np.mean(testRMSE))+'\n')


        #plt.plot(predicted, color='r' )
        #plt.plot(actual, color='b' )
        #plt.show()
    outfile.close()

if __name__ == "__main__": main()
