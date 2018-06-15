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

import java.util.Date;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlSchemaType;
import javax.xml.bind.annotation.XmlType;
import javax.xml.bind.annotation.adapters.CollapsedStringAdapter;
import javax.xml.bind.annotation.adapters.XmlJavaTypeAdapter;

/**
 * Information for ELIXIR internal purposes, maintained by ELIXIR Hub.
 * 
 * @author Dmitry Repchevsky
 */

@XmlType(name = "", propOrder = {"lastReviewExternalSab",
                                 "lastReviewElixirSab",
                                 "inSDP",
                                 "coreDataResource",
                                 "platform",
                                 "node",
                                 "comment"})
public class ElixirInfo {
    
    private Date lastReviewExternalSab;
    private Date lastReviewElixirSab;
    private boolean inSDP;
    private boolean isCoreDataResource;
    private ElixirPlatform platform;
    private ElixirNode node;
    private String comment;

    public Date getLastReviewExternalSab() {
        return lastReviewExternalSab;
    }

    public void setLastReviewExternalSab(Date lastReviewExternalSab) {
        this.lastReviewExternalSab = lastReviewExternalSab;
    }

    public Date getLastReviewElixirSab() {
        return lastReviewElixirSab;
    }

    public void setLastReviewElixirSab(Date lastReviewElixirSab) {
        this.lastReviewElixirSab = lastReviewElixirSab;
    }

    public boolean isInSDP() {
        return inSDP;
    }

    public void setInSDP(boolean inSDP) {
        this.inSDP = inSDP;
    }

    @XmlElement(name = "isCoreDataResource")
    public boolean isCoreDataResource() {
        return isCoreDataResource;
    }

    public void setCoreDataResource(boolean isCoreDataResource) {
        this.isCoreDataResource = isCoreDataResource;
    }

    public ElixirPlatform getPlatform() {
        return platform;
    }

    public void setPlatform(ElixirPlatform platform) {
        this.platform = platform;
    }

    public ElixirNode getNode() {
        return node;
    }

    public void setNode(ElixirNode node) {
        this.node = node;
    }

    @XmlSchemaType(name = "textType", namespace = "http://bio.tools")
    @XmlJavaTypeAdapter(CollapsedStringAdapter.class)
    public String getComment() {
        return comment;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }
}
