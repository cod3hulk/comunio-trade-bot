from BeautifulSoup import BeautifulSoup
import requests
import json
import argparse

def computeOffer(player):
    quotedPrice = player['quotedPrice']
    recommendedPrice = player['recommendedPrice']
    return int(recommendedPrice + ((quotedPrice - recommendedPrice) * 0.224))

def playerId(player):
    return "price[%s]" % player['playerId']

def placeOffer(players, session, communityId):
    for player in players:
        offerId = playerId(player)
        offer = computeOffer(player)
        data = {offerId:offer, 'action':'addOffer', 'makeoffer_x':'33', 'placedInCommunity':communityId}
        session.post("http://www.comunio.de/exchangemarket.phtml", data)
        print 'Placed offer [player:%s] [offer:%s]' % (player['playerName'], offer)

def shouldBuy(player):
    return ((player['quotedPrice'] - player['recommendedPrice']) > 20000) and not player['bid']

def main():
    #parse commandline arguments
    parser = argparse.ArgumentParser(description='Place comunio exchange offers automatically')
    parser.add_argument("username", help='username used for login')
    parser.add_argument("password", help='password used for login')
    args = parser.parse_args()

    # login
    s = requests.Session()
    data = { 'login': args.username, 'pass': args.password }
    r = s.post("http://www.comunio.de/login.phtml", data)

    # open exchange market
    r = s.get('http://www.comunio.de/exchangemarket.phtml')
    communityId = BeautifulSoup(r.text).find("input", {"name":"placedInCommunity"})["value"]

    ## get current players on transfer market
    r = s.get('http://www.comunio.de/rest/exchangeMarketService.php')
    players = json.loads(r.text)
    playersToBuy = [player for player in players if shouldBuy(player)]
    placeOffer(playersToBuy, s, communityId)

main()
