# Crypto related material for Quorum

This document lists the various crypto related material pertaining to a Quorum node.

#### Constellation
   * Two sets of key-pairs (e.g. arch_node.key,  arch_node.pub,  node.key and node.pub)
      * node.pub: ```u/uAHr9KPDpLHlHf8jqd+8s1315xjCN1Tl1gWuH/Kys=```
      * node.key: ```{"data":{"bytes":"L8iXhlI8kQP8rRFWhNXd+y5OYZwoI7+pSDIX9Yv7kLk="},"type":"unlocked"}```
    * The public key (node.pub) is used as parameter for the ```privatefor``` truffle flag to send private transactions to the Quorum network. the public key can be distributed freely.
   * TLS related client and server certificates and keys

#### Raft
   * No crypto material

#### Geth
   * One set of keypair (e.g. nodekey private key)
      * nodekey: ```364365b2ad72bd4a8d39e6555fe436d45f830bbe94665e0916cac0b404102291``` (64 chars)
      * The corresponding public key forms the node's enode: ```3ed506987cda275852854a9df4cee296fb7ce40d7027d03b13c0a2de8a2e61e76e986d67fee70e5de1545450c4799683c7b621e0aee4cd0144e1b0d9558e4109``` (128 chars)  
      * The enode + Geth IP + Geth listen port + Geth discovery port form the node's enode geth id: ```"enode://3ed506987cda275852854a9df4cee296fb7ce40d7027d03b13c0a2de8a2e61e76e986d67fee70e5de1545450c4799683c7b621e0aee4cd0144e1b0d9558e4109@172.13.0.2:30303?discport=0"```
      * The enode geth id + Raft port form the node's final enode id: 
```"enode://3ed506987cda275852854a9df4cee296fb7ce40d7027d03b13c0a2de8a2e61e76e986d67fee70e5de1545450c4799683c7b621e0aee4cd0144e1b0d9558e4109@172.13.0.2:30303?discport=0&raftport=50401"```

   * All enode related ids can be distributed freely.

   *  Atleast one set of account keypair(s). Without an account key (i.e the private key), Geth won't start.
      *  account: ```{"address":"5e2c1989e9e11b649eac9ddfabad30ef184bebaa","crypto":{"cipher":"aes-128-ctr","ciphertext":"9f06763baab716975359f95bacbb6228dddbd8fec265518938d63a832e1f4466","cipherparams":{"iv":"91f825650f7fb609010cec8af40fe80e"},"kdf":"scrypt","kdfparams":{"dklen":32,"n":262144,"p":1,"r":8,"salt":"f047687ef0f91e86e508ab7c1d8b816a51444d6ab4f9e2a26bf043e7d796dff0"},"mac":"cc8db1d20026a0ddb5b604417ae4e1befc4f41b5f85040acc07c92ed93eb5874"},"id":"4fe26b2e-13c9-4aeb-9a53-d171bfa34f7e","version":3}```

   *  When Truffle connects to a node, it uses the first account of the node by default to submit transactions, deploy contracts etc.

   *  The *address* portion above is the account (i.e wallet) public address and can be distributed freely.