/**
 * *****************************************************************************
 * Copyright (C) 2016 ELIXIR ES, Spanish National Bioinformatics Institute (INB)
 * and Barcelona Supercomputing Center (BSC)
 *
 * Modifications to the initial code base are copyright of their respective
 * authors, or their employers as appropriate.
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301  USA
 *****************************************************************************
 */

package es.elixir.bsc.biotools.parser.model;

import java.util.List;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlSchemaType;
import javax.xml.bind.annotation.XmlType;
import javax.xml.bind.annotation.adapters.CollapsedStringAdapter;
import javax.xml.bind.annotation.adapters.XmlJavaTypeAdapter;

/**
 * 
 * @author Dmitry Repchevsky
 */

@XmlType(name = "", propOrder = {"name",
                                 "version",
                                 "toolID",
                                 "doi",
                                 "shortDescription",
                                 "description",
                                 "homepage"})
public class Summary {

    private String name;
    private String version;
    private String toolID;
    private String doi;
    private String shortDescription;
    private String description;
    private String homepage;
    private List<String> mirrors;
    protected List<String> repositories;
    protected List<String> socialMedias;

    @XmlElement(required = true)
    @XmlSchemaType(name = "nameType", namespace = "http://bio.tools")
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @XmlJavaTypeAdapter(CollapsedStringAdapter.class)
    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    @XmlElement(required = true)
    @XmlSchemaType(name = "biotoolsIdType", namespace = "http://bio.tools")
    public String getToolID() {
        return toolID;
    }

    public void setToolID(String toolID) {
        this.toolID = toolID;
    }

    @XmlElement(required = true)
    @XmlSchemaType(name = "doiType", namespace = "http://bio.tools")
    public String getDoi() {
        return doi;
    }

    public void setDoi(String doi) {
        this.doi = doi;
    }

    public String getShortDescription() {
        return shortDescription;
    }

    public void setShortDescription(String shortDescription) {
        this.shortDescription = shortDescription;
    }

    @XmlSchemaType(name = "textType", namespace = "http://bio.tools")
    @XmlJavaTypeAdapter(CollapsedStringAdapter.class)
    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    @XmlElement(required = true)
    @XmlSchemaType(name = "urlType", namespace = "http://bio.tools")
    public String getHomepage() {
        return homepage;
    }

    public void setHomepage(String homepage) {
        this.homepage = homepage;
    }
}
