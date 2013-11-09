from itertools import combinations
from mrjob.job import MRJob

MIN_RATERS = 5
MIN_INTERSECTION = 5

class SemicolonValueProtocol(object):
    def write(self, key, values):
        return ';'.join(str(v) for v in values)

class PostFilter(MRJob): 

    OUTPUT_PROTOCOL = SemicolonValueProtocol

    def steps(self):
        return [
            self.mr(mapper=self.input, reducer=self.group_by_user_rating),
            self.mr(reducer=self.count_ratings_users_freq),
            self.mr(mapper=self.pairwise_items,
                    reducer=self.calculate_similarity),
            self.mr(mapper=self.calculate_ranking,
                    reducer=self.top_similar_items)]

    def input(self, key, line):
        #user_id, item_id, rating = line.split(',')
        #rating,item_id,user_id = line.split(',')
        vid, rating, item_id, user_id = line.split(',')
        yield item_id, (user_id, int(rating))

    def group_by_user_rating(self, key, values):
        total = 0
        final = []

        for user_id, rating in values:
            total += 1
            final.append((user_id, rating))

        if total < MIN_RATERS:
            return

        for user_id, rating in final:
            yield  user_id, (key, float(rating), total)

    def count_ratings_users_freq(self, user_id, values):
        item_count = 0
        item_sum = 0

        final = []

        for item_id, rating, ratings_count in values:
            item_count += 1
            item_sum += rating
            final.append((item_id, rating, ratings_count))

        yield user_id, (item_count, item_sum, final)

    def pairwise_items(self, user_id, values):
        item_count, item_sum, ratings = values

        for item1, item2 in combinations(ratings, 2):
            yield (item1[0], item2[0]), (item1[1], item2[1], item1[2], item2[2])

    def calculate_similarity(self, pair_key, lines):
        same_score = 0
        count = 0

        for score1, score2, item1Count, item2Count in lines:
            if (score1 == score2):
                same_score = same_score + 1

            count = count + 1

        if count < MIN_INTERSECTION:
            return

        yield pair_key, (float(same_score) / float(count), count)

    def calculate_ranking(self, item_keys, values):
        sim, n = values
        item_x, item_y = item_keys

        yield (item_x, sim), (item_y, n)

    def top_similar_items(self, key_sim, similar_ns):
        item_x, sim = key_sim
        for item_y, n in similar_ns:
            yield None, (item_x, item_y, sim, n)

if __name__ == '__main__':
    PostFilter.run()
