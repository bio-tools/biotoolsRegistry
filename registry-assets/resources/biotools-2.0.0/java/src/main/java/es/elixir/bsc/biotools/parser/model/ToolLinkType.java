package es.elixir.bsc.biotools.parser.model;

import javax.xml.bind.annotation.XmlEnum;
import javax.xml.bind.annotation.XmlEnumValue;

/**
 *
 * @author Dmitry Repchevsky
 */

@XmlEnum(EnumType.class)
public enum ToolLinkType {
    @XmlEnumValue("Browser") BROWSER("Browser"),
    @XmlEnumValue("Helpdesk") HELPDESK("Helpdesk"),
    @XmlEnumValue("Issue tracker") ISSUE_TRACKER("Issue tracker"),
    @XmlEnumValue("Mailing list") MAILING_LIST("Mailing list"),
    @XmlEnumValue("Mirror") MIRROR("Mirror"),
    @XmlEnumValue("Registry") REGISTRY("Registry"),
    @XmlEnumValue("Repository") REPOSITORY("Repository"),
    @XmlEnumValue("Social media") SOCIAL_MEDIA("Social media");
    
    private final String value;
    
    private ToolLinkType(String value) {
        this.value = value;
    }
    
    @Override
    public String toString() {
        return value;
    }

    public static ToolLinkType fromValue(String value) {
        for (ToolLinkType type: ToolLinkType.values()) {
            if (type.value.equals(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException(value);
    }
}
