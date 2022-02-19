import time
import blockcypher

'''
Block Cypher API Docs: https://www.blockcypher.com/dev/bitcoin/?python

To get your API key, sign up for an account: https://accounts.blockcypher.com/signup

Fill in your api key and run :)
'''

# The API key for BlockCypher
api_key = '405dbb2fb260460e99d9c37c6a5fc5c2'
# Whether to wait for transactions confirmations or not (it takes 5-6 min per transaction)
wait_for_transactions = True


def printBalances(wallet1, wallet2, api_key: str) -> None:
    '''
    Helper method for testing. Prints out various balances on wallets
    :param wallet1:
    :param wallet2:
    :param api_key: the blockcypher api key
    :return:
    '''

    # sleep for half a sec to slow us down cause of rate limiting
    time.sleep(0.5)

    print("\n###################################")

    # Get Balance in Satoshi
    addressDetails = blockcypher.get_address_overview(wallet1['address'], coin_symbol='bcy', api_key=api_key)
    print("[Wallet 1] Balance in Satoshi is total={}/confirmed={}/pending={}".format(addressDetails['final_balance'],
                                                                                     addressDetails['balance'],
                                                                                     addressDetails['unconfirmed_balance']))

    # Convert to BTC
    totalBalance = blockcypher.from_base_unit(addressDetails['final_balance'], 'btc')
    confirmedBalance = blockcypher.from_base_unit(addressDetails['balance'], 'btc')
    pendingBalance = blockcypher.from_base_unit(addressDetails['unconfirmed_balance'], 'btc')
    print("[Wallet 1] Balance in Bitcoin is total={}/confirmed={}/pending={}".format(totalBalance, confirmedBalance,
                                                                                     pendingBalance))

    # Get Balance in Satoshi
    addressDetails = blockcypher.get_address_overview(wallet2['address'], coin_symbol='bcy', api_key=api_key)
    print("[Wallet 2] Balance in Satoshi is total={}/confirmed={}/pending={}".format(addressDetails['final_balance'],
                                                                                     addressDetails['balance'],
                                                                                     addressDetails[
                                                                                         'unconfirmed_balance']))

    # Convert to BTC
    totalBalance = blockcypher.from_base_unit(addressDetails['final_balance'], 'btc')
    confirmedBalance = blockcypher.from_base_unit(addressDetails['balance'], 'btc')
    pendingBalance = blockcypher.from_base_unit(addressDetails['unconfirmed_balance'], 'btc')
    print("[Wallet 2] Balance in Bitcoin is total={}/confirmed={}/pending={}".format(totalBalance, confirmedBalance,
                                                                                     pendingBalance))

    print("###################################\n")


def satoshiToBTC(satoshi: int) -> int:
    '''
    Given an amount in Satoshi, converts it to Bitcoin
    :param satoshi: amount of satoshi
    :return: int representing the fee in bitcoin
    '''
    conversionFactor = 0.00000001
    return satoshi * conversionFactor


def getSatoshiFee(fee: int, txnSize: int) -> int:
    '''
    Given a fee per kb and transaction size converts to satoshi
    :param fee: the fee per kb
    :param txnSize: the txn size in mb
    :return: int representing the fee in satoshi
    '''
    # Converts Kb / b
    conversionFactor = 1000
    return fee / conversionFactor * txnSize


def waitForTxn(transactionId: str, api_key: str) -> None:
    '''
    Waits for the given transaction to have at least 6 confirmations
    :param transactionId: the hash of the transaction
    :param api_key: the blockcypher api key
    :return:
    '''

    transactionDetails = blockcypher.get_transaction_details(transactionId, coin_symbol='bcy', api_key=api_key)

    if ('error' in transactionDetails):
        print("Txn has not posted, was there some error")
        return

    # We want at least 6 confirmation to have confidence that the transaction has posted
    if (transactionDetails['confirmations'] < 6):
        print("Txn has less than 6 confirmations, waiting")
        startTime = time.time()
        while(transactionDetails['confirmations'] < 6):
            time.sleep(20)
            print("Txn has {} confirmations, waiting for 6...".format(transactionDetails['confirmations']))
            transactionDetails = blockcypher.get_transaction_details(transactionId, coin_symbol='bcy', api_key=api_key)
            if (time.time() - startTime > 600):
                print("Txn has not been confirmed in ten min, giving up")
                break

        print()
        print("Txn {} has been confirmed in {} sec".format(transactionId, time.time() - startTime))


if __name__ == '__main__':
    blockChainMetaData = blockcypher.get_blockchain_overview(coin_symbol='bcy', api_key=api_key)

    # Create a BTC wallet
    print("Creating Two Wallets")
    wallet1 = blockcypher.generate_new_address(coin_symbol='bcy', api_key=api_key)
    wallet2 = blockcypher.generate_new_address(coin_symbol='bcy', api_key=api_key)

    print("Wallet 1 address: {}, Wallet 2 address: {}".format(wallet1['address'], wallet2['address']))

    print("Block Explorer Addresses "
          "\n \tWallet 1: https://live.blockcypher.com/bcy/address/{}"
          "\n \tWallet2: https://live.blockcypher.com/bcy/address/{}"
          .format(wallet1['address'], wallet2['address']))

    printBalances(wallet1, wallet2, api_key)

    # Fund address with faucet, in satoshi (100 million satoshis to one bitcoin)
    # [1 BTC max per time - max 5 BTC per wallet]
    print("Funding Wallet 1 with 1 BTC")
    fundingTxn = blockcypher.send_faucet_coins(address_to_fund=wallet1['address'],
                                               satoshis=100000000,
                                               api_key=api_key,
                                               coin_symbol='bcy')

    print("Funding Transaction in Block Explorer: https://live.blockcypher.com/bcy/tx/{}".format(fundingTxn['tx_ref']))

    if (wait_for_transactions):
        printBalances(wallet1, wallet2, api_key)
        waitForTxn(fundingTxn['tx_ref'], api_key)

    printBalances(wallet1, wallet2, api_key)

    # send Money Over
    print("Sending 0.5 BTC from Wallet 1 to Wallet 2")
    print("Estimated Network Fee: {} BTC".format(satoshiToBTC(getSatoshiFee(blockChainMetaData['medium_fee_per_kb'], 226))))
    transaction = blockcypher.simple_spend(
        from_privkey=wallet1['private'],
        to_address=wallet2['address'],
        to_satoshis=50000000,
        coin_symbol='bcy',
        api_key=api_key)

    print("Transaction in Block Explorer: https://live.blockcypher.com/bcy/tx/{}".format(transaction))

    if (wait_for_transactions):
        printBalances(wallet1, wallet2, api_key)
        waitForTxn(transaction, api_key)

    printBalances(wallet1, wallet2, api_key)
