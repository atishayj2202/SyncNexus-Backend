DROP VIEW IF EXISTS payment_details;
CREATE VIEW payment_details AS
SELECT
    p.id AS id,
    p.created_at AS created_at,
    p.last_modified_at AS last_modified_at,
    p.approved_at AS approved_at,
    p.amount AS amount,
    p.currency AS currency,
    p.remarks AS remarks,
    p.from_user_id AS sender_id,
    sender.name AS sender_name,
    sender.phone_no AS sender_phone,
    sender.email AS sender_email,
    sender.user_type AS sender_user_type,
    p.to_user_id AS receiver_id,
    receiver.name AS receiver_name,
    receiver.phone_no AS receiver_phone,
    receiver.email AS receiver_email,
    receiver.user_type AS receiver_user_type
FROM payments p
JOIN user_accounts sender ON p.from_user_id = sender.id
JOIN user_accounts receiver ON p.to_user_id = receiver.id;
