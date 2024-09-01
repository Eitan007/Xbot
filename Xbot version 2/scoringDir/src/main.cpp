#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <regex>
#include <cmath>
#include <ctime>
#include <unordered_set>
#include <codecvt>
#include <locale>
#include <xlnt/xlnt.hpp>




// Define a structure to hold each row of data      ////////adjust here!!!!!!!!!!!!!!!!1
struct DataRow {
    std::string name;
    std::string username;
    std::string url;
    int followers;
    int following;
    int tweets;
    std::string bio;
    bool canDM;
    std::string location;
    std::string joinedX;
    bool translator;
    int likes;
    bool bluetick;
    bool defaultpic;
    int rawScore;
    int totalScore;


    // Constructor to initialize raw and total scores
    DataRow(int raw = 90, int total = 0) 
        : rawScore(raw), totalScore(total) {}
};

// is string character emoji?
bool isEmoji(char32_t codepoint) {
    // Check if the codepoint falls within the typical emoji Unicode ranges.
    return (codepoint >= 0x1F600 && codepoint <= 0x1F64F) ||  // Emoticons
           (codepoint >= 0x1F300 && codepoint <= 0x1F5FF) ||  // Miscellaneous Symbols and Pictographs
           (codepoint >= 0x1F680 && codepoint <= 0x1F6FF) ||  // Transport and Map Symbols
           (codepoint >= 0x2600 && codepoint <= 0x26FF)   ||  // Miscellaneous Symbols
           (codepoint >= 0x2700 && codepoint <= 0x27BF)   ||  // Dingbats
           (codepoint >= 0x1F900 && codepoint <= 0x1F9FF);    // Supplemental Symbols and Pictographs
}

// count emoji number in string
int countEmojis(const std::u32string& text) {
    int emojiCount = 0;
    for (char32_t ch : text) {
        if (isEmoji(ch)) {
            emojiCount++;
        }
    }
    return emojiCount;
}

// check emoji
int applyEmojiDeduction(const std::string& utf8_text, int currentScore) {
    // Convert UTF-8 to UTF-32
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter;
    std::u32string utf32_text = converter.from_bytes(utf8_text);

    // Count emojis
    int emojiCount = countEmojis(utf32_text);

    // Deduct 10 points if more than 3 emojis are found
    if (emojiCount > 3) {
        currentScore -= 10;
    }

    return currentScore;
}

// Deduction function
int apply_deduction(const DataRow& row) {
    // Define the list of states and countries
    const std::unordered_set<std::string> states_and_countries = {
        "Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan", "Islamabad Capital Territory",
        "Gilgit-Baltistan", "Azad Jammu and Kashmir",
        "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
        "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo",
        "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos",
        "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers",
        "Sokoto", "Taraba", "Yobe", "Zamfara",
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
        "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
        "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
        "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Nigeria", "Pakistan", "India"
    };

    // Define suspicious keywords and regex patterns
    std::vector<std::string> sus_keywords = {
        "crypto guru", "bitcoin millionaire", "NFT investor", "crypto airdrop",
        "blockchain expert", "free tokens", "get rich quick", "DM for collab",
        "giveaway", "earn money from home", "make money fast", "follow for follow",
        "100% legit", "guaranteed earnings", "passive income", "affiliate marketer",
        "join my team", "work from home", "entrepreneur", "business opportunity",
        "influencer", "brand ambassador", "model", "verified", "official",
        "user123456789", "click the link", "free giveaway", "no risk", "double your money",
        "instant access"
    };

    std::regex user_regex("^user\\d+[a-zA-Z0-9]+$", std::regex::icase);

    int value = row.rawScore;

    // Check if 'Username' contains any suspicious keywords
    std::string username_lower = row.username;
    std::transform(username_lower.begin(), username_lower.end(), username_lower.begin(), ::tolower);
    for (const auto& keyword : sus_keywords) {
        if (username_lower.find(keyword) != std::string::npos || row.username.find(keyword) != std::string::npos) {
            value -= 10;
            break;
        }
    }

    // Check if 'Username' matches the suspicious pattern
    if (std::regex_match(row.username, user_regex)) {
        value -= 10;
    }

    // Check if 'Bio' contains more than 3 emojis
    value = applyEmojiDeduction(row.bio, value);

    // Check the Followers/Following ratio
    if (row.followers > 0) {
        double ratio = static_cast<double>(row.following) / row.followers;
        if (ratio > 10) {
            value -= 10;
        } else if (ratio >= 3) {
            value -= 5;
        }
    }

    // Check the number of Tweets
    if (row.tweets < 10) {
        value -= 10;
    } else if (row.tweets < 50) {
        value -= 5;
    }

    // Check if 'Can_DM' is True
    if (row.canDM) {
        value -= 5;
    }

    // Check if the location matches any word in the flagged list
    if (states_and_countries.find(row.location) != states_and_countries.end()) {
        value -= 5;  // Deduct 5 points if a match is found
    }

    // Check account age based on 'Joined_X'
    // struct tm tm = {};
    // std::istringstream ss(row.joinedX);
    // ss >> std::get_time(&tm, "%Y-%m-%d %H:%M:%S");
    // time_t joined_time = mktime(&tm);
    // time_t now = time(nullptr);
    // double age = difftime(now, joined_time) / (60 * 60 * 24 * 365); // Convert to years

    // if (age < 1) {
    //     if (age < 0.5) {
    //         value -= 10;
    //     } else {
    //         value -= 5;
    //     }
    // }




     // Parsing the date-time from the "joinedX" string (ignoring timezone)
    int year, month, day, hour, minute, second;
    if (sscanf(row.joinedX.c_str(), "%4d-%2d-%2d %2d:%2d:%2d", &year, &month, &day, &hour, &minute, &second) == 6) {
        struct tm tm = {};
        tm.tm_year = year - 1900;  // tm_year is years since 1900
        tm.tm_mon = month - 1;     // tm_mon is 0-based
        tm.tm_mday = day;
        tm.tm_hour = hour;
        tm.tm_min = minute;
        tm.tm_sec = second;
        time_t joined_time = mktime(&tm);
        time_t now = time(nullptr);
        double age = difftime(now, joined_time) / (60 * 60 * 24 * 365);  // Convert to years

        if (age < 1) {
            if (age < 0.5) {
                value -= 10;
            } else {
                value -= 5;
            }
        }
    }



    return value;
}

// Final score calculation function
int calculate_final_score(const DataRow& row, double scoring_factor) {
    return std::round(scoring_factor * row.rawScore);
}

// Function to read, process, and save the CSV data
void scoreData(const std::string& input_file_path, const std::string& output_file_path, double scoring_factor) {
    std::ifstream file(input_file_path);
    std::string line;
    std::vector<DataRow> data;

    // Read header
    std::getline(file, line);

    // Read each row
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        DataRow row;

        // Read each field                              ///adjust here!!!!!!!!!!!!
            std::getline(ss, row.name, ',');
            std::getline(ss, row.username, ',');
            std::getline(ss, row.url, ',');
        try{
            std::getline(ss, line, ','); row.followers = std::stoi(line);
        } catch (const std::exception &e) {
            std::cout << "follower failed" << output_file_path << std::endl;
        }
        try{
            std::getline(ss, line, ','); row.following = std::stoi(line);
        } catch (const std::exception &e) {
            std::cout << "following failed" << output_file_path << std::endl;
        }
        try{
            std::getline(ss, line, ','); row.tweets = std::stoi(line);
        } catch (const std::exception &e) {
            std::cout << "tweets failed" << output_file_path << std::endl;
        }
            std::getline(ss, row.bio, ','); 
            std::getline(ss, line, ','); row.canDM = (line == "1");
            std::getline(ss, row.location, ',');
            std::getline(ss, row.joinedX, ',');
            std::getline(ss, line, ','); row.translator = (line == "1");
        try{
            std::getline(ss, line, ','); row.likes = std::stoi(line);
        } catch (const std::exception &e) {
            std::cout << "likes failed" << output_file_path << std::endl;
        }
            std::getline(ss, line, ','); row.bluetick = (line == "1");
            std::getline(ss, line, ','); row.defaultpic = (line == "1");
        try{
            std::getline(ss, line, ','); row.rawScore = std::stoi(line);
        } catch (const std::exception &e) {
            std::cout << "rawScore failed" << output_file_path << std::endl;
        }
        try{
            std::getline(ss, line, ','); row.totalScore = std::stoi(line);
        } catch (const std::exception &e) {
            std::cout << "All failed" << output_file_path << std::endl;
        }
    
        // Apply deductions and calculate scores
        row.rawScore = apply_deduction(row);
        row.totalScore = calculate_final_score(row, scoring_factor);

        // Add to data vector
        data.push_back(row);
    }

    // Close the input file
    file.close();

    // Write results to a new CSV file              //adjust here!!!!!!!!!!!!!!!!!!!!!!!!!!1111
    std::ofstream output_file(output_file_path);
    output_file << "Name,Username,Url,Followers,Following,Tweets,Bio,Can_DM,Location,Joined_X,Translator,Likes,BlueTick,DefaultPic,RawScore,TotalScore\n";
    
    for (const auto& row : data) {
        output_file << row.username << ","
                    << row.url << ","
                    << row.followers << ","
                    << row.following << ","
                    << row.tweets << ","
                    << row.totalScore << "\n";
    }

    std::cout << "Results saved to " << output_file_path << std::endl;

    // Close the output file
    output_file.close();

}

//main function
int main(int argc, char *argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input_csv_file_path> <output_csv_file_path>" << std::endl;
        return 1;
    }

    std::string input_file_path = argv[1];
    std::string output_file_path = argv[2];
    //double scoring_factor = std::stod(argv[3]);


    const double scoring_factor = 1.1112;

    scoreData(input_file_path, output_file_path, scoring_factor);
    
    return 0;
}














// for updating the deprecated emoji analyzer



// #include <string>
// #include <vector>
// #include <Windows.h>

// std::wstring utf8_to_utf16(const std::string& utf8_text) {
//     int wchars_num = MultiByteToWideChar(CP_UTF8, 0, utf8_text.c_str(), -1, NULL, 0);
//     std::wstring utf16_text(wchars_num, 0);
//     MultiByteToWideChar(CP_UTF8, 0, utf8_text.c_str(), -1, &utf16_text[0], wchars_num);
//     return utf16_text;
// }


// std::u32string utf16_to_utf32(const std::wstring& utf16_text) {
//     std::vector<char32_t> utf32_buffer(utf16_text.size());
//     std::u32string utf32_text;

//     int utf32_len = 0;
//     for (wchar_t wchar : utf16_text) {
//         if (wchar >= 0xD800 && wchar <= 0xDBFF) {
//             // High surrogate
//             continue;
//         } else if (wchar >= 0xDC00 && wchar <= 0xDFFF) {
//             // Low surrogate
//             continue;
//         } else {
//             utf32_buffer[utf32_len++] = static_cast<char32_t>(wchar);
//         }
//     }

//     utf32_text.assign(utf32_buffer.begin(), utf32_buffer.begin() + utf32_len);
//     return utf32_text;
// }

// // Combine conversions
// std::u32string utf8_to_utf32(const std::string& utf8_text) {
//     std::wstring utf16_text = utf8_to_utf16(utf8_text);
//     return utf16_to_utf32(utf16_text);
// }
