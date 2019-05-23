# -*- coding:utf-8 -*-
from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import BlockChain

app = Flask(__name__)
node_identifier = str(uuid4()).replace("-", "")
blockchain = BlockChain()


@app.route("/mine", method=["GET"])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block["proof"]  # 324984774000, 工作量证明 - 答案
    proof = blockchain.proof_of_work(last_proof)

    # 挖矿成功的奖励(sender=0)
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)

    # 生成最新区块
    block = blockchain.new_block(proof)
    response = {
        "message": "new block forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"]
    }

    return jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.json()
    required = ["sender", "recipient", "amount"]
    if not all(i in values for i in required):
        return "missing values", 400

    index = blockchain.new_transaction(values["sender"], values["recipient"], values["amount"])
    response = {'message': f'transaction will be added to block {index}'}

    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9088)
