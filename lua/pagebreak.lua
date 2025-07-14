-- pagebreak.lua
-- A pandoc filter to implement page breaks in docx output

function newpage()
    if FORMAT == 'docx' then
      return pandoc.RawBlock('openxml', 
        '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
    end
    return nil
  end
  
  function Para(el)
    -- Match paragraphs containing only \newpage or similar
    if #el.content == 1 and el.content[1].text == '\\newpage' then
      return newpage()
    end
    return el
  end
  
  function Header(el)
    -- Optional: Add page breaks before specified header levels
    -- Uncomment and modify the level check as needed
    -- if el.level == 1 then
    --   return {newpage(), el}
    -- end
    return el
  end
  
  -- Return the filter as a table of functions
  return {
    Para = Para,
    Header = Header
  }