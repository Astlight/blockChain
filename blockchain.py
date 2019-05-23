# -*- coding:utf-8 -*-
import hashlib
import json
from time import time
from urllib.parse import urlparse

from pip._vendor import requests


class BlockChain():
    def __init__(self):
        self.chain = []  # 区块list
        self.current_transactions = []  # 交易list
        # 创世区块
        self.new_block(previous_hash=1, proof=100)
        # 节点
        self.nodes = set()

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)  # ip

    def new_block(self, proof, previous_hash=None):
        """
        生成新块
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        # 重置 交易list
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })
        return self.last_block["index"] + 1  # 最近的chain中的index + 1

    # hash上一block存在新块
    @staticmethod
    def hash(block):
        """
        生成块的 SHA-256 hash值
        :param block: <dict> Block
        :return: <str>
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # 属性
    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    # 挖矿
    @staticmethod
    def valid_proof(last_proof, proof):
        """
        验证证明: 是否hash(last_proof, proof)以4个0开头?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # 检查是否是有效链，遍历每个块验证 hash 和 proof。 在resole_conflicts中使用
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]  # 初始块在服务启动时生成(previous_hash=1, proof=100)
        current_index = 1  # 第二块开始校验区块正确性
        while current_index < len(chain):
            block = chain[current_index]

            # 校验前后块hash
            if block["previous_hash"] != self.hash(last_block):
                return False

            # 校验前后块proof
            if not self.valid_proof(last_block["proof"], block["proof"]):
                return False

            last_block = block

        return True

    def resolve_conflicts(self):
        """
        共识算法解决冲突
        使用网络中最长的链.
        :return: <bool> True 如果链被取代, 否则为False
        """
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            # 在各节点中请求或寻找最长的链
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json.get("length")
                chain = response.json.get("chain")

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


'''
block = {  
    'index': 1,   # 索引
    'timestamp': 1506057125.900785,   # Unix 时间戳
    'transactions': [   # 交易列表
        {  
            'sender': "8527147fe1f5426f9dd545de4b27ee00",  
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",  
            'amount': 5,  
        }  
    ],  
    'proof': 324984774000,   # 工作量证明
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824" #前一个区块的 Hash 值  
}
https://www.cnblogs.com/chendongsheng/p/8537496.html 
'''
