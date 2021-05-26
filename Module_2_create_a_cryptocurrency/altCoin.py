import uuid
from flask import Flask, jsonify, request
import datetime
import hashlib
import json
import requests
from uuid import uuid4
from urllib.parse import urlparse

from werkzeug.wrappers import response

class Transaction:
   def __init__(self, sender, reciever, amount):
      self.sender = sender
      self.reciever = reciever
      self.amount = amount

   def serialize(self):
      return {
         "sender":self.sender,
         "reciever":self.reciever,
         "amount":self.amount
      }
 
class Blockchain:
   def __init__(self):
      self.chain = []
      self.transactions = set()
      self.nodes = set()
      self.create_block(proof=1,previous_hash='1')

   def create_block(self, proof, previous_hash):
      block = {
         'index':len(self.chain) + 1,
         'timestamp':str(datetime.datetime.now()),
         'proof':proof,
         'previous_hash':previous_hash, 
         "transactions":[e.serialize() for e in self.transactions] 
      }
      self.transactions = set()
      self.chain.append(block)
      return block

   def get_previous_block(self):
      if len(self.chain) > 0:
         return self.chain[-1]
      else:
         return None

   def proof_of_work(self, previous_proof):
      nounce = 1
      check_proof = False
      while check_proof is False:
         hash_operation = hashlib.sha256((str(nounce**2 - previous_proof**2)).encode()).hexdigest()
         print(hash_operation)
         if hash_operation[:4] == "0000":
            check_proof=True
         else:
            nounce+=1
      return nounce

   def hash(self, block):
      encoded_block = json.dumps(block, sort_keys=True).encode()
      print(encoded_block)
      return hashlib.sha256(encoded_block).hexdigest()

   def is_chain_valid(self, chain):
      index = len(self.chain) - 1
      while index >= 1:
         block = self.chain[index]
         prevBlock = self.chain[index-1]
         proof = block["proof"]
         blockHash = hashlib.sha256(str(proof**2 - prevBlock["proof"]**2).encode()).hexdigest()
         if block["previous_hash"] != self.hash(prevBlock):
            return False
         if blockHash[:4] != "0000":
            return False
         index -= 1
      return True

   def mine_block(self):
      proof = self.proof_of_work(self.chain[-1]["proof"])
      prevHash = self.hash(self.chain[-1])
      self.create_block(proof, prevHash)

   def add_transaction(self, sender, reciever, amount):
      transaction = Transaction(sender, reciever, amount)
      self.transactions.add(transaction)
      return len(self.chain)+1

   def add_node(self, address):
      parse_url = urlparse(address)
      self.nodes.add(parse_url)

   def replace_chain(self):
      network = self.nodes
      max_chain = None
      length = len(self.chain)
      for node in network:
         node_chain = self.__getNodeChain(node)
         if node_chain and len(node_chain) > length and self.is_chain_valid(node_chain):
            max_chain = node_chain
            length = len(node_chain)
      if max_chain:
         self.chain = max_chain
         return True
      return False
   
   def __getNodeChain(self, address):
      r = requests.get(f'http://{address}/get_blockchain')
      if r.status_code != 201:
         return None
      else:
         response = r.json()
         return response['blockchain']
      

   def __str__(self):
      for i in self.chain:
         transaction={
            "proof":i["proof"],
            "transactions":i["transactions"],
            "index":i["index"]
         }
         print(transaction)
      return ""




# Creating a Web App
app = Flask(__name__)

address = str(uuid4()).replace("-","")

blockchain = Blockchain()


# --- Part 1 --- Mine a block
# Mine a new block
@app.route("/mine_block", methods=["GET"])
def mine_block():
   previous_block = blockchain.get_previous_block()
   previous_proof = previous_block["proof"]
   previous_hash = blockchain.hash(previous_block)
   proof = blockchain.proof_of_work(previous_proof)
   blockchain.add_transaction(sender= address,reciever= "Ahmed",amount= 12)
   block = blockchain.create_block(proof, previous_hash)
   response = {"message":"Successfully Mined!", "block":{
      "index": block["index"],
      "timestamp": block["timestamp"],
      "proof": block["proof"],
      "transactions":block["transactions"],
      "previous_hash": block["previous_hash"]
   }}
   return jsonify(response), 201

# Check blockchain validation
@app.route("/is_valid", methods=["GET"])
def is_valid():
   validation = blockchain.is_chain_valid(blockchain.chain)
   response={
      "validation":validation
   }
   return jsonify(response),200

# Get full blockchain
@app.route("/get_blockchain", methods=["GET"])
def get_blockchain():
   response = {
      'message':"Full blockchain",
      "length": len(blockchain.chain),
      "blockchain":blockchain.chain
   }
   return jsonify(response), 200

# --- Part 2 --- Add Transaction
# Add a transaction to the blockchain
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
   transaction = request.json
   index = blockchain.add_transaction(transaction["sender"],transaction["reciever"],transaction["amount"])
   response={
      "message": f'Transaction added to {index}',
      "sender":transaction["sender"],
      "amount":transaction["amount"],
      "reviever":transaction["reciever"]
   }
   return  jsonify(response), 200

# Get all transactions added to the block
@app.route("/get_transactions")
def get_transactions():
   response={
      "message":f"list of transaction from the node {address}",
      "transactions":[e.serialize() for e in list(blockchain.transactions)]
   }
   return jsonify(response),200

# --- Part 3 --- Decentralization ---

# Connect the nodes
@app.route("/connect_node", methods=["POST"])
def connect_node():
   json = request.get_json()
   nodes = json.get("nodes")
   if not nodes:
      return "Node does not exist", 401
   for node in nodes:
      print(node)
      blockchain.add_node(node)
   response={"message":"Nodes added", 
               "totalNodes":len(blockchain.nodes)}
   return jsonify(response), 201
      
      
# Replacing the chain by the longest blockchain
@app.route("/replace_chain ", methods=["GET"])
def replace_chain():
   is_chain_replaced = blockchain.replace_chain()
   if is_chain_replaced:
      response = {
         "message":"The chain has been replaced"
      }
   else:
      response = {
         'message':'The chain is the longest one'
      }
   return jsonify(response), 200


if __name__ == "__main__":
   app.run(host = "0.0.0.0", port=5000, debug=True)
