# L(i)T Codes
Experiments with fountain codes

## CS 166 Final Project on Fountain Codes
## By Madeline Liao, Kendrick Shen, and Sean Decker
The code in this repo was written to help us understand how how to implement fountain codes, namely LT codes and RaptorQ for as primitives in a transfer protocol over sockets. To test these protocols, we built a toy network in which we were able to control the noise of the channel.

We wrote all the code in this rpositor except for the code in the directories: ./libRaptorQ-0.1.X, ./resources_to_send, and ./resources_received. The resources directories really just hold various files that we tested our transfer protocol on. The network simulation, lt encoding and decoding, and the communication protocol were all implemented by us.

## How it works
* The sender encodes some input into a series of packets to be sent over the lossy channel. The sender's is some file supplied in ./resources_to_send
* The sender sends the packets over a lossy channel in which packets are lost with programable probability
* The receiver receives the packets and decodes the packets it receives into a file of the same name as that which was sent and places the created file in ./resources_received

## Running the program
To run the program enter `python ./run.py -<proto>`into your terminal where proto is either, udp, rq, or lt. proto defines which protocol the sender and receiver will run to send resources. The file which is sent and the loss of the channel can be changed in ./run.py.

You can also run both the sender and receiver in seperate terminal windows using `python ./sender.py -<proto>` and `python ./receiver.py -<proto>`.

Note that this program is written in python 2.7, so you must configure your environment as such for the code to work.

## Jupyter Notebook
Alos note that there are various jupyter notebooks in the repo which give a more clear picture of how our implementation of LT codes works.
