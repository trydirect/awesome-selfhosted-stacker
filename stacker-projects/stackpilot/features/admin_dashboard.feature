Feature: Admin Dashboard API
  As an administrator
  I want to manage the knowledge base and monitor conversations
  So that I can ensure the AI assistant is working correctly

  Scenario: Stats endpoint returns correct structure
    Given the API is running
    When I request "/api/admin/stats"
    Then the response should contain "total_documents"
    And the response should contain "total_conversations"
    And the response should contain "total_websites"

  Scenario: Documents endpoint returns list
    Given the API is running
    When I request "/api/admin/documents"
    Then the response should contain "documents"
    And the response should contain "total"

  Scenario: Ollama status endpoint works
    Given the API is running
    When I request "/api/admin/ollama/status"
    Then the response should contain "healthy"
    And the response should contain "models"

  Scenario: Login with correct password succeeds
    Given the API is running
    When I login with password from environment
    Then the response should be 200

  Scenario: Dashboard serves HTML
    Given the API is running
    When I request "/api/admin/dashboard"
    Then the response should be 200
    And the response should contain "StackPilot"
