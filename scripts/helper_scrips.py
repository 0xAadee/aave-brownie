from brownie import accounts, network, config

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    elif id:
        return accounts.get(id)
    elif (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
          or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    elif network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None
