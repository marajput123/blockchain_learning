from flask import Flask, jsonify
import datetime
import hashlib
import base64
import json


# Part 1 - Building a Blockchain

#--------------------------------------------------------------------------------------------------------
# class Blockchain:

#    def __init__(self):
#       self.chain = []
#       self.proof_of_work(previous_hash='0')

#    def create_block(self, next_hash, previous_hash = "0" , proof = 1, data = "no data"):
#       block = {
#          'index':len(self.chain) + 1,
#          'timestamp':str(datetime.datetime.now()),
#          'proof':proof,
#          'data':data,
#          'previous_hash':previous_hash, 
#          'hash': next_hash
#       }

#       self.chain.append(block)
#       return block

#    def get_previous_block(self):
#       if len(self.chain) > 0:
#          return self.chain[-1]
#       else:
#          return None

#    def proof_of_work(self, previous_hash):
#       nounce = 1
#       is_hashed = False
#       hash_key = "000000"
#       new_hash=""
#       h = hashlib
#       print(previous_hash)
#       while not is_hashed:
#          new_hash = (h.sha256((previous_hash + str(nounce)).encode())).hexdigest()
#          print(nounce, ":",new_hash)
#          if new_hash[:len(hash_key)] == hash_key:
#             is_hashed = True
#          else:
#             nounce+=1
#       self.create_block(new_hash,previous_hash,nounce,"transaction")

#    def __str__(self):
#       for i in self.chain:
#          print(i)
#       return ""


# blockchain = Blockchain()
# blockchain.proof_of_work(blockchain.chain[-1]["hash"])
# blockchain.proof_of_work(blockchain.chain[-1]["hash"])
#------------------------------------------------------------------------------------------------------

class Blockchain:

   def __init__(self):
      self.chain = []
      self.create_block(proof=1,previous_hash='1')

   def create_block(self, proof, previous_hash):
      block = {
         'index':len(self.chain) + 1,
         'timestamp':str(datetime.datetime.now()),
         'proof':proof,
         'data':" ",
         'previous_hash':previous_hash, 
      }

      self.chain.append(block)
      return block

   def get_previous_block(self):
      if len(self.chain) > 0:
         return self.chain[-1]
      else:
         return None

   def proof_of_work(self, previous_proof):
      new_proof = 1
      check_proof = False
      while check_proof is False:
         hash_operation = hashlib.sha256((str(new_proof**2 - previous_proof**2)).encode()).hexdigest()
         if hash_operation[:4] == "0000":
            check_proof=True
         else:
            new_proof+=1
      return new_proof


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



   def __str__(self):
      for i in self.chain:
         print(i)
      return ""




# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)
blockchain = Blockchain()

# Mine a new block
@app.route("/mine_block", methods=["GET"])
def mine_block():
   # blockchain.mine_block()
   # print(blockchain)
   previous_block = blockchain.get_previous_block()
   previous_proof = previous_block["proof"]
   previous_hash = blockchain.hash(previous_block)
   proof = blockchain.proof_of_work(previous_proof)
   block = blockchain.create_block(proof, previous_hash)
   

   response = {"message":"Successfully Mined!", "block":{
      "index": block["index"],
      "timestamp": block["timestamp"],
      "proof": block["proof"],
      "data":block["data"],
      "previous_hash": block["previous_hash"]
   }}

   return jsonify(response), 201

# Get full blockchain
@app.route("/get_blockchain", methods=["GET"])
def get_blockchain():
   response = {
      'message':"Full blockchain",
      "blockchain":blockchain.chain,
      "length": len(blockchain.chain)
   }
   return jsonify(response), 200


@app.route("/is_valid", methods=["GET"])
def is_valid():
   validation = blockchain.is_chain_valid(blockchain.chain)
   response={
      "validation":validation
   }
   return jsonify(response),200

if __name__ == "__main__":
   app.run(host = "0.0.0.0", port=4000, debug=True)