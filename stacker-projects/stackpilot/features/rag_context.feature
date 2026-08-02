Feature: RAG Context Building
  As the RAG pipeline
  I want to build context from search results
  So that the LLM can generate informed responses

  Scenario: Empty results produce fallback message
    Given I have no search results
    When I build context
    Then the context should be "No relevant knowledge base entries found."

  Scenario: Single result is formatted correctly
    Given I have 1 search result with title "Pricing" and source "https://example.com/pricing"
    When I build context
    Then the context should contain "[Source 1: Pricing]"
    And the context should contain "relevance:"
    And the context should contain "https://example.com/pricing"

  Scenario: Multiple results are separated by dividers
    Given I have 3 search results
    When I build context
    Then the context should contain "[Source 1:"
    And the context should contain "[Source 2:"
    And the context should contain "[Source 3:"
    And the context should contain "---"

  Scenario: Missing title falls back to source
    Given I have 1 search result with title "" and source "https://example.com/about"
    When I build context
    Then the context should contain "[Source 1: https://example.com/about]"
