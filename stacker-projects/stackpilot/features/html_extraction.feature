Feature: HTML Text Extraction
  As a crawler
  I want to extract readable text from HTML pages
  So that the knowledge base contains clean content

  Scenario: Extract text from simple HTML
    Given I have HTML "<html><body><p>Hello world</p></body></html>"
    When I extract text
    Then the text should contain "Hello world"

  Scenario: Strip script tags
    Given I have HTML "<html><body><p>Hello</p><script>alert('hi')</script><p>World</p></body></html>"
    When I extract text
    Then the text should contain "Hello"
    And the text should contain "World"
    And the text should not contain "alert"

  Scenario: Strip style tags
    Given I have HTML "<html><head><style>.red{color:red}</style></head><body><p>Content</p></body></html>"
    When I extract text
    Then the text should contain "Content"
    And the text should not contain "color"

  Scenario: Extract title
    Given I have HTML "<html><head><title>My Page</title></head><body></body></html>"
    When I extract title
    Then the title should be "My Page"

  Scenario: Missing title returns empty
    Given I have HTML "<html><body>No title here</body></html>"
    When I extract title
    Then the title should be ""

  Scenario: Extract links from HTML
    Given I have HTML with links "href='/about'" and "href='https://example.com/contact'"
    When I extract links from base "https://example.com"
    Then I should get 2 links

  Scenario: Skip non-http links
    Given I have HTML with link "href='mailto:test@example.com'"
    When I extract links from base "https://example.com"
    Then I should get 0 links
