Feature: Text Chunking
  As a developer
  I want the knowledge base to split text into manageable chunks
  So that embeddings can be created for semantic search

  Scenario: Empty text produces no chunks
    Given I have text ""
    When I chunk the text
    Then I should get 0 chunks

  Scenario: Short text stays in one chunk
    Given I have text "Hello world"
    When I chunk the text
    Then I should get 1 chunks
    And chunk 0 should be "Hello world"

  Scenario: Long text is split into multiple chunks
    Given I have text of 600 characters
    When I chunk the text with chunk_size 500 and overlap 100
    Then I should get 2 chunks

  Scenario: Chunks overlap by the specified amount
    Given I have text of 1000 characters
    When I chunk the text with chunk_size 500 and overlap 100
    Then chunk 0 should end with the same 100 characters that chunk 1 starts with

  Scenario: Whitespace is normalized
    Given I have text "  Hello   world  "
    When I chunk the text
    Then chunk 0 should be "Hello world"
