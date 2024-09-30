To add minimize, maximize, and close buttons to your custom Vaadin dashboard component, you can enhance the widget structure by creating a header section for each widget. This header will contain the buttons along with the title. Here's how to do that step by step:

### Step 1: Update the Widget Creation Method

Modify the `createWidget` method in your `DashboardView` class to include the buttons.

#### Updated `DashboardView.java`

```java
package com.example;

import com.vaadin.flow.component.button.Button;
import com.vaadin.flow.component.html.Div;
import com.vaadin.flow.component.orderedlayout.HorizontalLayout;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.router.Route;

@Route("")
public class DashboardView extends VerticalLayout {

    public DashboardView() {
        setPadding(true);
        setSpacing(true);

        // Create a header for the dashboard
        Div header = new Div();
        header.setText("Dashboard");
        header.addClassName("dashboard-header");
        add(header);

        // Create a layout for the widgets
        HorizontalLayout widgetContainer = new HorizontalLayout();
        widgetContainer.setWidth("100%");

        // Add some custom widgets
        for (int i = 1; i <= 3; i++) {
            Div widget = createWidget("Widget " + i);
            widgetContainer.add(widget);
        }

        add(widgetContainer);
    }

    private Div createWidget(String title) {
        Div widget = new Div();
        widget.addClassName("dashboard-widget");
        widget.setWidth("200px");
        widget.setHeight("150px");
        
        // Create header for the widget
        HorizontalLayout headerLayout = new HorizontalLayout();
        headerLayout.setWidthFull();
        headerLayout.addClassName("widget-header");

        Div titleLabel = new Div();
        titleLabel.setText(title);
        titleLabel.addClassName("widget-title");
        
        // Minimize button
        Button minimizeButton = new Button("_", e -> {
            widget.setVisible(!widget.isVisible());
        });

        // Maximize button
        Button maximizeButton = new Button("[]", e -> {
            widget.setHeight(widget.getHeight().equals("150px") ? "300px" : "150px");
        });

        // Close button
        Button closeButton = new Button("X", e -> {
            widget.setVisible(false);
        });

        // Add buttons to the header
        headerLayout.add(titleLabel, minimizeButton, maximizeButton, closeButton);
        widget.add(headerLayout);

        // Set up the content area
        Div content = new Div();
        content.setText("Content for " + title);
        content.addClassName("widget-content");
        widget.add(content);

        // Add styles for buttons
        minimizeButton.getStyle().set("margin-left", "auto");
        maximizeButton.getStyle().set("margin-left", "5px");
        closeButton.getStyle().set("margin-left", "5px");

        return widget;
    }
}
```

### Step 2: Add Styles

Add some styles for the header and buttons to your `styles.css` file:

```css
.dashboard-header {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}

.dashboard-widget {
    background-color: #f9f9f9;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
    border-radius: 8px;
    overflow: hidden; /* Ensure no overflow from rounded corners */
}

.widget-header {
    background-color: #eaeaea;
    padding: 10px;
    align-items: center;
}

.widget-title {
    flex-grow: 1; /* Allow title to take available space */
}

.widget-header button {
    cursor: pointer;
    background: transparent;
    border: none;
    font-size: 16px;
}

.widget-content {
    padding: 10px;
}
```

### Step 3: Run Your Application

With the updated code and styles, run your application again:

```bash
mvn clean install
mvn jetty:run
```

### Summary

Now your dashboard component includes minimize, maximize, and close buttons on each widget. The buttons allow users to hide the widget, toggle its height, and remove it from view. You can further customize the styles and functionality according to your needs.

If you have any other features in mind or need additional help, feel free to ask!
