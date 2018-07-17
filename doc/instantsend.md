## InstantSend Technical Information

InstantSend has been integrated into the Core Daemon in two ways:
* "push" notifications (ZMQ and `-instantsendnotify` cmd-line/config option);
* RPC commands.

#### ZMQ

When a "Transaction Lock" occurs the hash of the related transaction is broadcasted through ZMQ using both the `zmqpubrawtxlock` and `zmqpubhashtxlock` channels.

* `zmqpubrawtxlock`: publishes the raw transaction when locked via InstantSend
* `zmqpubhashtxlock`: publishes the transaction hash when locked via InstantSend

This mechanism has been integrated into Bitcore-Node-Dash which allows for notification to be broadcast through Insight API in one of two ways:
* WebSocket: [https://github.com/dashpay/insight-api-dash#web-socket-api](https://github.com/dashpay/insight-api-dash#web-socket-api)
* API: [https://github.com/dashpay/insight-api-dash#instantsend-transactions](https://github.com/dashpay/insight-api-dash#instantsend-transactions)

#### Command line option

When a wallet InstantSend transaction is successfully locked a shell command provided in this option is executed (`%s` in `<cmd>` is replaced by TxID):

```
-instantsendnotify=<cmd>
```

#### RPC

Details pertaining to an observed "Transaction Lock" can also be retrieved through RPC, it’s important however to understand the underlying mechanism.

There is a field named `instantlock` (that is present in commands such as `listsinceblock`). The value in this field indicates whether a given transaction is locked via InstantSend.

**Examples**

1. `listsinceblock`
    * InstantSend transaction just occurred:
        * confirmations: 0
        * instantlock: true
    * InstantSend transaction received one confirmation from blockchain:
        * confirmations: 1
        * instantlock: true
    * non-InstantSend transaction just occurred:
        * confirmations: 0
        * instantlock: false
    * non-InstantSend transaction received one confirmation from blockchain:
        * confirmations: 1
        * instantlock: false
