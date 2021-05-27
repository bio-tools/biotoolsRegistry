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

import java.util.ArrayList;
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

@XmlType(name = "", propOrder = {"toolTypes",
                                 "topics",
                                 "goTermIDs",
                                 "soTermIDs",
                                 "taxIds",
                                 "operatingSystems",
                                 "languages",
                                 "license",
                                 "collectionIDs",
                                 "maturity",
                                 "cost",
                                 "accessibility",
                                 "statuses"})
public class Labels {

    private List<ToolType> toolTypes;
    private List<Topic> topics;
    private List<String> goTermIDs;
    private List<String> soTermIDs;
    private List<String> taxIds;
    private List<OperatingSystemType> operatingSystems;
    private List<LanguageType> languages;
    private LicenseType license;
    private List<String> collectionIDs;
    private MaturityType maturity;
    private CostType cost;
    private List<AccessibilityType> accessibility;
    private List<LicenseStatusType> statuses;

    @XmlElement(name = "toolType", required = true)
    public List<ToolType> getToolTypes() {
        if (toolTypes == null) {
            toolTypes = new ArrayList<>();
        }
        return toolTypes;
    }

    @XmlElement(name = "topic", required = true)
    public List<Topic> getTopics() {
        if (topics == null) {
            topics = new ArrayList<>();
        }
        return topics;
    }

    @XmlElement(name = "goTermID")
    @XmlJavaTypeAdapter(CollapsedStringAdapter.class)
    public List<String> getGoTermIDs() {
        if (goTermIDs == null) {
            goTermIDs = new ArrayList<>();
        }
        return goTermIDs;
    }

    @XmlElement(name = "soTermID")
    @XmlJavaTypeAdapter(CollapsedStringAdapter.class)
    public List<String> getSoTermIDs() {
        if (soTermIDs == null) {
            soTermIDs = new ArrayList<>();
        }
        return soTermIDs;
    }

    @XmlElement(name = "taxId")
    @XmlJavaTypeAdapter(CollapsedStringAdapter.class)
    public List<String> getTaxIds() {
        if (taxIds == null) {
            taxIds = new ArrayList<>();
        }
        return taxIds;
    }

    @XmlElement(name = "operatingSystem")
    public List<OperatingSystemType> getOperatingSystems() {
        if (operatingSystems == null) {
            operatingSystems = new ArrayList<>();
        }
        return operatingSystems;
    }

    @XmlElement(name = "language")
    public List<LanguageType> getLanguages() {
        if (languages == null) {
            languages = new ArrayList<>();
        }
        return languages;
    }

    public LicenseType getLicense() {
        return license;
    }

    public void setLicense(LicenseType license) {
        this.license = license;
    }

    @XmlElement(name = "collectionID")
    @XmlSchemaType(name = "biotoolsCollectionIdType", namespace = "http://bio.tools")
    public List<String> getCollectionIDs() {
        if (collectionIDs == null) {
            collectionIDs = new ArrayList<>();
        }
        return collectionIDs;
    }

    @XmlElement(name = "maturity")
    public MaturityType getMaturity() {
        return maturity;
    }
    
    public void setMaturity(MaturityType maturity) {
        this.maturity = maturity;
    }
    
    @XmlElement(name = "cost")
    public CostType getCost() {
        return cost;
    }
    
    public void setCost(CostType cost) {
        this.cost = cost;
    }
    
    @XmlElement(name = "accessibility")
    public List<AccessibilityType> getAccessibility() {
        if (accessibility == null) {
            accessibility = new ArrayList<>();
        }
        return accessibility;
    }
    
    @XmlElement(name = "status")
    public List<LicenseStatusType> getStatuses() {
        if (statuses == null) {
            statuses = new ArrayList<>();
        }
        return statuses;
    }
}