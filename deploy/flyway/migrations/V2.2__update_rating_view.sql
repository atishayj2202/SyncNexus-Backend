DROP VIEW IF EXISTS avg_rating_with_comments;
CREATE VIEW avg_rating_with_comments AS
SELECT user_to                                   as id,
       MIN(created_at)                           AS created_at,
       MAX(last_modified_at)                     AS last_modified_at,
       AVG(rate)                                 AS rate,
       json_object_agg(user_from::TEXT, comment) AS comments,
       COUNT(*)                                  AS count
FROM rating
GROUP BY user_to;