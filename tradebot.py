from BeautifulSoup import BeautifulSoup
import requests
import json
import argparse

class Bot:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def run(self):
        self.login()
        players = self.players()
        self.placeOffer(players)

    def login(self):
        self.session = requests.Session()
        data = { 'login': self.username, 'pass': self.password }
        r = self.session.post("http://www.comunio.de/login.phtml", data)

    def players(self):
        r = self.session.get('http://www.comunio.de/exchangemarket.phtml')
        self.communityId = BeautifulSoup(r.text).find("input", {"name":"placedInCommunity"})["value"]

        r = self.session.get('http://www.comunio.de/rest/exchangeMarketService.php')
        players = json.loads(r.text)

        return [player for player in players if self.shouldBuy(player)]

    def shouldBuy(self, player):
        return ((player['quotedPrice'] - player['recommendedPrice']) > 20000) and not player['bid']

    def placeOffer(self, players):
        for player in players:
            offerId = self.playerId(player)
            offer = self.computeOffer(player)
            data = {offerId:offer, 'action':'addOffer', 'makeoffer_x':'33', 'placedInCommunity':self.communityId}
            self.session.post("http://www.comunio.de/exchangemarket.phtml", data)
            print 'Placed offer [player:%s] [offer:%s]' % (player['playerName'], offer)

    def computeOffer(self, player):
        quotedPrice = player['quotedPrice']
        recommendedPrice = player['recommendedPrice']
        return int(recommendedPrice + ((quotedPrice - recommendedPrice) * 0.224))

    def playerId(self, player):
        return "price[%s]" % player['playerId']


def main():
    # parse commandline arguments
    parser = argparse.ArgumentParser(description='Place comunio exchange offers automatically')
    parser.add_argument("username", help='username used for login')
    parser.add_argument("password", help='password used for login')
    args = parser.parse_args()

    bot = Bot(args.username, args.password)
    bot.login()
    players = bot.players()

    bot.placeOffer(players)

main()
