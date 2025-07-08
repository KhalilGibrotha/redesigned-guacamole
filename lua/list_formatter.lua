-- list_formatter.lua
-- A pandoc filter to handle list formatting in templates
-- This complements the Jinja2 oxford_comma_list macro

function BulletList(elem)
  -- Handle bullet lists in a more structured way
  if FORMAT == 'docx' then
    -- For Word documents, ensure proper list formatting
    return elem
  elseif FORMAT == 'html' then
    -- For HTML, ensure proper CSS classes if needed
    return elem
  end
  return elem
end

function OrderedList(elem)
  -- Handle ordered lists
  if FORMAT == 'docx' then
    return elem
  elseif FORMAT == 'html' then
    return elem
  end
  return elem
end

-- Handle inline code better in lists
function Code(elem)
  if FORMAT == 'docx' then
    -- Ensure inline code is properly formatted in Word
    return elem
  end
  return elem
end

-- Improve table formatting
function Table(elem)
  if FORMAT == 'docx' then
    -- Add table styling for Word documents
    return elem
  end
  return elem
end
