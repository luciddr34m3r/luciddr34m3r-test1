<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
    <html>
        <body>
            <h2>Games</h2>
            <xsl:for-each select="boardgames/boardgame">
            <div><xsl:value-of select="yearpublished"></div>
        </body>
    </html>

