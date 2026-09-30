-- =============================================================================
-- Flipkart Analytics Hub - Read-Only Database User Setup
-- =============================================================================
-- Creates a dedicated user with SELECT permissions only.
-- The dashboard and API backend must NEVER have INSERT/UPDATE/DELETE/DROP privileges.
-- =============================================================================

CREATE USER IF NOT EXISTS 'flipkart_readonly'@'%' IDENTIFIED BY 'ReadOnly_SecurePass123!';

-- Grant SELECT only on the flipkart_analytics database
GRANT SELECT ON flipkart_analytics.* TO 'flipkart_readonly'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify privileges
SHOW GRANTS FOR 'flipkart_readonly'@'%';
