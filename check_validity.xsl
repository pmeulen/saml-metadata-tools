<?xml version="1.0" encoding="UTF-8"?>

<!-- Check whether a metadata file is valid for at least 15 more minutes by looking at the validUntil 
     attribute of the EntityDescriptor or the EntitiesDescriptor root element.
     The XML file thst is tested must have an EntityDescriptor or EntitiesDescriptor root element.
     If no validUntil attribute is present the metadata is presumed valid
     Outputs a message with terminate="yes" when the check fails, not output otherwise
    
     Note: This uses XSLT extensions from http://exslt.org/date/index.html 
           This XSLT stylesheet is intended to be used with xsltproc http://xmlsoft.org/XSLT/ 

     Usage: xmlproc check_validity.xsl <metadata.xml> 
-->   

<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    xmlns:date="http://exslt.org/dates-and-times"
    extension-element-prefixes="date"
    version="1.0">
    
    <xsl:output method="text"/>
    
    <!-- Recurse down through all elements by default -->
    <xsl:template match="*">
        <xsl:apply-templates select="node()|@*"/>
    </xsl:template>    
    
    <!-- Overrite build in templates and do not output text blocks, comments and attributes -->
    <xsl:template match="text()|comment()|@*"/>
         
    <xsl:template match="/">
        <xsl:if test="count(/md:EntitiesDescriptor|/md:EntityDescriptor)!=1">
            <xsl:message terminate="yes">
                <xsl:text>[ERROR] Root element must be EntitiesDescriptor or EntityDescriptor. Found: </xsl:text>
                <xsl:value-of select="name(/*)"/>
            </xsl:message>            
        </xsl:if>
        <xsl:apply-templates></xsl:apply-templates>
    </xsl:template>    
    
    <xsl:template match="/md:EntitiesDescriptor|/md:EntityDescriptor
        [@validUntil]
        ">
        <!--
            * add(xs:dateTime, xs:duration): retuns xs:dateTime
            Adds a duration to datetime
            
            * date:difference(xs:dateTime, xs:dateTime): returns xs:duration
            When the 2nd date > than the first date the returned duration is negative, and starts with -P...
            
            Check that the datetime in the validUntil attrubute is valid for at least 15 more minutes
            Strings offsets in XPath are base-1: so substring(string, 1, 1) returns the first character in string
        -->                
        <xsl:if test="substring(date:difference(date:add(date:date-time(), 'PT15M'), @validUntil), 1, 1) = '-'">
            <xsl:message terminate="yes">
                <xsl:text>[ERROR] Metadata expired. Metadata must be valid for at least 15 more minutes. The validUntil attribute on the Entit(y|ies)Descriptor is '</xsl:text>
                <xsl:value-of select="@validUntil"/>
                <xsl:text>' the current time is </xsl:text>
                <xsl:value-of select="date:date-time()"/>
            </xsl:message>
        </xsl:if>
    </xsl:template>
        
</xsl:stylesheet>