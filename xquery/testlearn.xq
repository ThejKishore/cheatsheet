xquery version "3.0";

(:~
: User: thej
: Date: 4/3/18
: Time: 10:08 PM
: To change this template use File | Settings | File Templates.
:)

(:declare variable $stringtokenlist := fn:tokenize("a-b-c-d-e","-");:)

declare function local:checkContains( $value as xs:string, $list as xs:string*) as xs:string+
{
    for $value1 in $list
    return if(contains($value,$value1)) then($value1) else ("nothing")

};


declare function local:returnxmltitle($value as node() ) as xs:string+
{
    let $valueToReturn :=""
    return
        if($value/@category/string() = "XML") then ( $value/title/string()) else ("")

};


let  $stringtokenlist := fn:tokenize("a-b-c-d-e","-")
let  $dataValue:="defgh"
return (local:checkContains($dataValue,$stringtokenlist))

(:for $book in (doc("./xquerysamples/Books.xml")/books/book)
return
    (local:returnxmltitle($book)):)





