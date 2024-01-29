CREATE VIEW avg_rating_with_comments AS
SELECT user_to,
       AVG(rate)                                 AS rate,
       json_object_agg(user_from::TEXT, comment) AS comments
FROM rating
GROUP BY user_to;
