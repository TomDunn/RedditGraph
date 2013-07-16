class Submission:

    def __init__(self, row):
        self.id         = row[0]
        self.subreddit  = row[1]
        self.title      = row[2]
        self.domain     = row[3]
        self.url        = row[4]
        self.is_self    = row[5]
        self.selftext   = row[6]
        self.score      = row[7]
        self.ups        = row[8]
        self.downs      = row[9]
        self.num_comments = row[10]
        self.over_18    = row[11]
        self.created_utc= row[12]
        self.scrape_time= row[13]

    def is_x_post(self):
        return self.domain == 'reddit.com' and not self.is_self and 'r' in self.url.split('/')

    def get_sub_from_url(self):
        splitted = self.url.split('/')
        try:
            return splitted[splitted.index('r') + 1]
        except ValueError:
            print self.url, ' ', self.domain, ' ', self.title, ' ', self.is_self
            return "poo_poo_platter"
        except IndexError:
            print "no subreddit"
            print self
            return "poo_poo_platter"

    def is_self_post(self):
        return self.is_self == 1

    def __str__(self):
        return """
            id:\t{id}
            sub:\t{sub}
            title:\t{title}
            url:\t{url}
            is_self:\t{is_self}
        """.format(id=self.id, sub=self.subreddit, title=self.title, dom=self.domain, url=self.url, is_self=self.is_self)
