# Time Zone Calling Rules

**Effective:** 2026-01-09

## The Westward Expansion Rule

As the day progresses (Eastern Time), expand calling westward:

| ET Time | Call These Time Zones |
|---------|----------------------|
| 9 AM - 12 PM | Eastern (FL, GA, NY) |
| 12 PM - 3 PM | Central (TX, IL, MO) |
| 3 PM - 6 PM | Mountain (CO, AZ, NM) |
| 6 PM - 9 PM | Pacific (CA, WA, OR) |

## Implementation

```python
def get_target_timezone(current_hour_et: int) -> str:
    if current_hour_et < 12:
        return "Eastern"  # FL, GA, NY, etc.
    elif current_hour_et < 15:
        return "Central"  # TX, IL, etc.
    elif current_hour_et < 18:
        return "Mountain"  # CO, AZ, etc.
    else:
        return "Pacific"  # CA, WA, etc.
```

## Why This Matters

- Calls at appropriate local time (business hours)
- Don't call Pacific at 6 AM their time
- Don't call Eastern at 9 PM their time
- Respects recipient's schedule = better answer rate

## State Mappings

### Eastern (UTC-5)

Florida, Georgia, New York, Virginia, North Carolina, South Carolina, Ohio, Pennsylvania, etc.

### Central (UTC-6)

Texas, Illinois, Missouri, Tennessee, Alabama, Louisiana, Oklahoma, etc.

### Mountain (UTC-7)

Colorado, Arizona, New Mexico, Utah, Wyoming, etc.

### Pacific (UTC-8)

California, Washington, Oregon, Nevada
