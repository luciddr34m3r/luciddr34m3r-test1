import cgi
import urllib
import os
import urllib2

from google.appengine.api import users, urlfetch
from google.appengine.ext import ndb

import xml.dom.minidom

import webapp2
import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
    
API_BASE_PATH = "http://www.boardgamegeek.com/"
    
class MainPage(webapp2.RequestHandler):

    def getText(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def handleBoardgames(self, boardgames):
        boardgames = boardgames.getElementsByTagName("boardgame")
        
        # List of dicts
        # name, thumbnail, description, players, time
        bgs = []
        indexes = ["name", "description", "thumbnail", "maxplayers", "minplayers", "playingtime"]
        
        # For each game returned, we need to build our dictionary
        for boardgame in boardgames:
            bg_info = {}
        
            # We need to get all the values we care about
            for index in indexes:
                #print index
                # Gotta handle a couple edge cases
                
                # The name field can have multiple names, we only want to pull the primary name
                if index == "name":
                    for name in boardgame.getElementsByTagName(index):
                        if name.hasAttribute("primary"):
                            if name.getAttribute("primary") == "true":
                                bg_info[index] = self.getText(name.childNodes)
                                
                # If it isn't the name field, we only really have to return the text and we are done
                else:
                    element = boardgame.getElementsByTagName(index)
                    if element:
                        bg_info[index] = self.getText(element[0].childNodes)
                    else:
                        bg_info[index] = ""
                        
            print bg_info
            bgs.append(bg_info)        
                                
                
        return bgs

            

    def handleItems(self, items): 

        bgs = []

        items = items.getElementsByTagName("item")
        
        bg_ids = []
        bg_id_list =""
        
        for item in items:
            if item.getAttribute("type") == "boardgame":
                bg_name = item.getElementsByTagName("name")[0].getAttribute("value")
                bg_id = item.getAttribute("id")
                
                bg_ids.append(bg_id)
                
                bgs.append({"name": bg_name, "id": bg_id}) 
                #print bg_id
                
        for bg_id in bg_ids:
            if bg_id != "41047":
                bg_id_list += bg_id + ","
            
        print bg_id_list
        
        url = API_BASE_PATH + "xmlapi/boardgame/" + bg_id_list
        game_details = urllib.urlopen(url)
        gd_dom = xml.dom.minidom.parseString(game_details.read())
        
        
        # This returns a full list of info we care about. A list of dicts
        return self.handleBoardgames(gd_dom)
                

    def get(self):
        urlfetch.set_default_fetch_deadline(45)
        template_values = {}

        # Default search-string value
        bg_list = self.request.get('bg-search-string',
                                          "")

        template_values["search_term"] = bg_list        

        if bg_list:
            # Grab a list of the boardgames that match your search string
            params = {"query" : bg_list, "type" : "boardgame"}
            print params
            url = API_BASE_PATH + "xmlapi2/search/" + "?" + urllib.urlencode(params)
            print url
            q_result = urllib.urlopen(url)
            print "good1"
            
            # Make it parseable
            dom = xml.dom.minidom.parseString(q_result.read())
            print "good2"
            
            # Handle all items. This includes the nested query for more information on each boardgame. 
            # In the end we want a list with:
            # name, thumbnail, description, players, time
            template_values["games"] = self.handleItems(dom)

        else:
            pass

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))



application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)






















