Feature: Chat Widget API
  As a website visitor
  I want to ask questions and get AI-powered answers
  So that I can find information quickly

  Scenario: Send a chat message and receive a response
    Given the API is running
    When I send a chat message "What is your pricing?"
    Then I should receive a reply
    And the response should have a session_id
    And the response should have a confidence score

  Scenario: Chat message creates a conversation
    Given the API is running
    When I send a chat message "Hello" with session_id "test-session-1"
    Then a conversation should exist with session_id "test-session-1"

  Scenario: Widget.js is served as JavaScript
    Given the API is running
    When I request "/api/widget/widget.js"
    Then the response should have content-type "text/plain" or "application/javascript"
    And the response should contain "stackpilot"
